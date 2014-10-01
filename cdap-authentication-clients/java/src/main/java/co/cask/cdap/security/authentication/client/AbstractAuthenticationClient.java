/*
 * Copyright © 2014 Cask Data, Inc.
 *
 * Licensed under the Apache License, Version 2.0 (the "License"); you may not
 * use this file except in compliance with the License. You may obtain a copy of
 * the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
 * WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
 * License for the specific language governing permissions and limitations under
 * the License.
 */


package co.cask.cdap.security.authentication.client;

import co.cask.cdap.common.conf.Constants;
import co.cask.cdap.common.http.HttpRequest;
import co.cask.cdap.common.http.HttpRequestConfig;
import co.cask.cdap.common.http.HttpRequests;
import co.cask.cdap.common.http.HttpResponse;
import co.cask.cdap.common.http.ObjectResponse;
import co.cask.cdap.common.http.exception.HttpFailureException;
import com.google.common.collect.Multimap;
import com.google.common.reflect.TypeToken;
import org.apache.commons.lang.StringUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;
import java.net.HttpURLConnection;
import java.net.URI;
import java.util.Date;
import java.util.List;
import java.util.Map;
import java.util.Random;
import java.util.concurrent.TimeUnit;

/**
 * Abstract authentication client implementation with common methods.
 */
public abstract class AbstractAuthenticationClient implements AuthenticationClient {
  private static final Logger LOG = LoggerFactory.getLogger(AbstractAuthenticationClient.class);

  private static final Random RANDOM = new Random();
  private static final String AUTH_URI_KEY = "auth_uri";
  private static final String HTTP_PROTOCOL = "http";
  private static final String HTTPS_PROTOCOL = "https";
  private static final String ACCESS_TOKEN_KEY = "access_token";
  private static final String EXPIRES_IN_KEY = "expires_in";
  private static final String TOKEN_TYPE_KEY = "token_type";
  private static final long SPARE_TIME_IN_MILLIS = 5000;

  private long expirationTime;
  private AccessToken accessToken;
  private URI baseURI;
  private URI authURI;
  private Boolean authEnabled;
  private boolean verifySSLCert;

  /**
   * Returns HTTP headers required for authentication.
   */
  protected abstract Multimap<String, String> getAuthenticationHeaders();

  @Override
  public void invalidateToken() {
    accessToken = null;
  }

  @Override
  public boolean isAuthEnabled() throws IOException {
    if (authEnabled == null) {
      String strAuthURI = fetchAuthURI();
      authEnabled = StringUtils.isNotEmpty(strAuthURI);
      if (authEnabled) {
        authURI = URI.create(strAuthURI);
      }
    }
    return authEnabled;
  }

  @Override
  public void setConnectionInfo(String host, int port, boolean ssl) {
    if (baseURI != null) {
      throw new IllegalStateException("Connection info is already configured!");
    }
    baseURI = URI.create(String.format("%s://%s:%d%s/ping", ssl ? HTTPS_PROTOCOL : HTTP_PROTOCOL, host, port,
                                       Constants.Gateway.GATEWAY_VERSION));
  }

  @Override
  public AccessToken getAccessToken() throws IOException {
    if (!isAuthEnabled()) {
      throw new IOException("Authentication is disabled in the gateway server.");
    }

    if (accessToken == null || isTokenExpired()) {
      long requestTime = System.currentTimeMillis();
      accessToken = fetchAccessToken();
      expirationTime = requestTime + TimeUnit.SECONDS.toMillis(accessToken.getExpiresIn()) - SPARE_TIME_IN_MILLIS;
      LOG.debug("Received the access token successfully. Expiration date is {}.", new Date(expirationTime));
    }
    return accessToken;
  }

  /**
   * @return the authentication server URL or empty value if authentication is not enabled in the gateway server
   */
  protected URI getAuthURI() {
    return authURI;
  }

  public boolean isVerifySSLCert() {
    return verifySSLCert;
  }

  protected void setVerifySSLCert(boolean verifySSLCert) {
    this.verifySSLCert = verifySSLCert;
  }

  /**
   * Checks if the access token has expired.
   *
   * @return true, if the access token has expired
   */
  private boolean isTokenExpired() {
    return expirationTime < System.currentTimeMillis();
  }

  /**
   * Fetches the available authentication server URL, if authentication is enabled in the gateway server,
   * otherwise, empty string will be returned.
   *
   * @return string value of the authentication server URL
   * @throws IOException IOException in case of a problem or the connection was aborted or if url list is empty
   */
  private String fetchAuthURI() throws IOException {
    if (baseURI == null) {
      throw new IllegalStateException("Connection information not set!");
    }

    LOG.debug("Try to get the authentication URI from the gateway server: {}.", baseURI);
    HttpResponse response = HttpRequests.execute(HttpRequest.get(baseURI.toURL()).build(), getHttpRequestConfig());

    LOG.debug("Got response {} - {} from {}", response.getResponseCode(), response.getResponseMessage(), baseURI);
    if (response.getResponseCode() != HttpURLConnection.HTTP_UNAUTHORIZED) {
      return "";
    }

    Map<String, List<String>> responseMap =
      ObjectResponse.fromJsonBody(response,
                                  new TypeToken<Map<String, List<String>>>() { }).getResponseObject();
    LOG.debug("Response map from gateway server: {}", responseMap);

    String result;
    List<String> uriList = responseMap.get(AUTH_URI_KEY);
    if (uriList != null && !uriList.isEmpty()) {
      result = uriList.get(RANDOM.nextInt(uriList.size()));
    } else {
      throw new IOException("Authentication servers list is empty.");
    }
    return result;
  }

  /**
   * Executes fetch access token request.
   *
   * @param request the http request to fetch access token from the authentication server
   * @return {@link AccessToken} object containing the access token
   * @throws IOException IOException in case of a problem or the connection was aborted or if the access token is not
   * received successfully from the authentication server
   */
  private AccessToken execute(HttpRequest request) throws IOException {
    HttpResponse response = HttpRequests.execute(request, getHttpRequestConfig());

    LOG.debug("Got response {} - {} from {}", response.getResponseCode(), response.getResponseMessage(), baseURI);
    if (response.getResponseCode() != HttpURLConnection.HTTP_OK) {
      throw new HttpFailureException(response.getResponseMessage(), response.getResponseCode());
    }

    Map<String, String> responseMap =
      ObjectResponse.fromJsonBody(response, new TypeToken<Map<String, String>>() { }).getResponseObject();
    String tokenValue = responseMap.get(ACCESS_TOKEN_KEY);
    String tokenType = responseMap.get(TOKEN_TYPE_KEY);
    String expiresInStr = responseMap.get(EXPIRES_IN_KEY);

    LOG.debug("Response map from auth server: {}", responseMap);

    if (StringUtils.isEmpty(tokenValue) || StringUtils.isEmpty(tokenType) || StringUtils.isEmpty(expiresInStr)) {
      throw new IOException("Unexpected response was received from the authentication server.");
    }

    return new AccessToken(tokenValue, Long.valueOf(expiresInStr), tokenType);
  }

  private AccessToken fetchAccessToken() throws IOException {
    LOG.debug("Authentication is enabled in the gateway server. Authentication URI {}.", getAuthURI());

    return execute(HttpRequest.get(getAuthURI().toURL())
                     .addHeaders(getAuthenticationHeaders())
                     .build()
    );
  }

  private HttpRequestConfig getHttpRequestConfig() {
    return new HttpRequestConfig(0, 0, isVerifySSLCert());
  }
}
