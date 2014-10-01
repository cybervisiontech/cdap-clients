# Authentication Client Python API

The Authentication Client Python API is for fetching the access token from the authentication server when writing
external Python applications.

## Supported Actions

 - Fetch an access token from the authentication server with credentials supported by the active authentication mechanism;
 - Check if authentication is enabled in the gateway server; and
 - Invalidate any cached access tokens. 
 
 Current implementation supports three authentication mechanisms:
 - Basic Authentication
 - LDAP
 - JAASPI

## Installation
 To install CDAP Authentication Client, run:
```
    $ python setup.py install
```

## Usage

 To use the Authentication Client Python API, include these imports in your Python script:

```
    from cdap_auth_client import Config
    from cdap_auth_client import BasicAuthenticationClient
```

## Example
   
 Create a BasicAuthenticationClient instance:
 
 ```
   authentication_client = BasicAuthenticationClient()
 ```
      
 Set the connection parameters: authentication server host; authentication server host port; SSL mode:
 
 ```
   authentication_client.set_connection_info('localhost', 10000, False)
 ```
 
 Create the configuration file structure in JSON format:
 
 ```
  {
    "security_auth_client_username": "admin",
    "security_auth_client_password": "secret",
    "security_ssl_cert_check": true
  }
 ```  
 
 Load configuration from JSON File:
 
 ```
 config = Config().read_from_file('auth_config.json')
 ```
 
 Or set the required fields in the ```Config``` object:
 ```
 config = Config()
 config.security_auth_client_username = "admin"
 config.security_auth_client_password = "secret"
 config.security_ssl_cert_check = True
 ```
 
 Configure the authentication client with the ```Config``` object:
 ```
 authentication_client.configure(config)
 ```
 
 Check if authentication is enabled in the gateway server:
 
 ```
  is_enabled = authentication_client.is_auth_enabled()
 ``` 
                      
 Retrieve the access token from the authentication server:
 
 ```
 token = authentication_client.get_access_token()
 ```



 