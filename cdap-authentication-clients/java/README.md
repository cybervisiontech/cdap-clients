authentication-client-java
==========================

The Authentication Client Java API is for fetching the access token from the authentication server.

## Supported Actions

 - fetch an access token from the authentication server with credentials supported by the active authentication 
   mechanism;
 - check that authentication is enabled in the gateway server.

 Current implementation supports three authentication mechanisms:
  - Basic Authentication;
  - LDAP;
  - JAASPI.
 
 Also, is possible to extend existing logic and implement a custom client for any other authentication 
 mechanisms. To create a new authentication client, implement the ```AuthenticationClient``` interface.   

## Build
 
 To build the Authentication Client Java API jar, use:

 ```mvn package``` or ``` mvn package -DskipTests```

## Usage

 To use the Authentication Client Java API, include this Maven dependency in your project's ```pom.xml``` file:
 
 <dependency>
  <groupId>co.cask.cdap</groupId>
  <artifactId>cdap-authentication-client</artifactId>
  <version>1.0.0</version>
 </dependency>
 
## Example
   
Create a ```BasicAuthenticationClient``` instance by full class name:
 
 ```
  String authClientClassName = "co.cask.cdap.security.authentication.client.basic.BasicAuthenticationClient";
  AuthenticationClient authenticationClient = configuration.getClassByName(authClientClassName);
 ```
 
Set the gateway server connection info (this method needs calling only once for every ```AuthenticationClient```
 object):
  - the gateway server hostname;
  - the gateway server port;
  - the boolean flag, ```true``` if SSL is enabled in the gateway server.
 
 ```
  authenticationClient.setConnectionInfo("localhost", 10000, false);
 ```
  
Configure the authentication client with additional properties (this method should be called only once for every
 ```AuthenticationClient``` object):
 
 ```
  authenticationClient.configure(properties);
 ```

**Note:**

 - The ```BasicAuthenticationClient``` supports these properties:

 ```
  security.auth.client.username=username
  security.auth.client.password=password
 ```

 - When SSL is enabled, to allow self-signed certificates set `security.auth.client.verify.ssl.cert=false`.
 
Check if authentication is enabled in the gateway server:
 
 ```
  boolean isEnabled = authenticationClient.isAuthEnabled();
 ```                      
 
Get the access token for the user from the authentication server:
 
 ```  
   String token = authenticationClient.getAccessToken();  
 ```
 If an access token is not available, an ```IOException``` will be thrown. 
 
 
Retrieve credentials required by the authentication provider from the authentication server:

 ```
   List<Credential> credentials = authenticationClient.getRequiredCredentials();
 ```

**Note:** Interactive clients can use this list to obtain credentials from the user and then configure
 the ```authenticationClient```:
 
 ```
   for(Credential cred : credentials) {
     config.set(credentials.getName(), credValue);
   }
   authenticationClient.configure(config);
 ```
