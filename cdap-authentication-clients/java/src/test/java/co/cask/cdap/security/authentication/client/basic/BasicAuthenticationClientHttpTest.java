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

package co.cask.cdap.security.authentication.client.basic;

import com.google.common.collect.ImmutableList;
import com.google.common.collect.ImmutableSet;
import org.junit.AfterClass;
import org.junit.BeforeClass;

/**
 *
 */
public class BasicAuthenticationClientHttpTest extends BasicAuthenticationClientTestBase {
  @BeforeClass
  public static void setUp() throws Exception {
    sslEnabled = false;
    authServer = new TestHttpService(ImmutableSet.of(new AuthServer()), sslEnabled);
    authServer.startAndWait();

    authEnabledRouter = new TestHttpService(ImmutableSet.of(
      new Router(true, ImmutableList.of(
        String.format("%s://%s:%d/token",
                      sslEnabled ? "https" : "http",
                      authServer.getBindAddress().getHostName(),
                      authServer.getBindAddress().getPort())
      ))), sslEnabled);
    authEnabledRouter.startAndWait();

    authDisabledRouter = new TestHttpService(ImmutableSet.of(new Router(false, ImmutableList.<String>of())),
                                             sslEnabled);
    authDisabledRouter.startAndWait();

    noAuthServerRouter = new TestHttpService(ImmutableSet.of(new Router(true, ImmutableList.<String>of())), sslEnabled);
    noAuthServerRouter.startAndWait();
  }

  @AfterClass
  public static void tearDown() {
    if (authEnabledRouter != null) {
      authEnabledRouter.stopAndWait();
    }

    if (authServer != null) {
      authServer.stopAndWait();
    }

    if (authDisabledRouter != null) {
      authDisabledRouter.stopAndWait();
    }

    if (noAuthServerRouter != null) {
      noAuthServerRouter.stopAndWait();
    }
  }
}
