"""
Authentication endpoints for login and token management
"""
import cherrypy
import logging
from .auth.middleware import require_auth

logger = logging.getLogger(__name__)


class AuthAPIEndpoints:
    """Nested endpoint for /api/auth/* RESTful routes"""
    
    def __init__(self):
        # Create tokens nested endpoint for /api/auth/tokens
        self.tokens = TokensAPIEndpoint()


class TokensAPIEndpoint:
    """RESTful token management endpoints for /api/auth/tokens"""
    
    @cherrypy.expose
    @cherrypy.tools.json_out()
    @require_auth
    def index(self):
        # Handle CORS preflight
        if cherrypy.request.method == 'OPTIONS':
            return {}
        
        # Get token manager from cherrypy config
        token_manager = cherrypy.config.get('token_manager')
        if not token_manager:
            cherrypy.response.status = 500
            return {'success': False, 'error': 'Token manager not available'}
        
        if cherrypy.request.method == 'GET':
            try:
                tokens = token_manager.list_tokens()
                return {
                    'success': True,
                    'tokens': tokens
                }
            except Exception as e:
                logger.error(f"Token list error: {e}")
                cherrypy.response.status = 500
                return {
                    'success': False,
                    'error': 'Failed to list tokens'
                }
        
        elif cherrypy.request.method == 'POST':
            try:
                import json
                body = cherrypy.request.body.read().decode('utf-8')
                data = json.loads(body) if body else {}
                name = data.get('name', '').strip()
                
                if not name:
                    cherrypy.response.status = 400
                    return {
                        'success': False,
                        'error': 'Token name is required'
                    }
                
                # Create the token
                token_id, plaintext_token = token_manager.create_token(name)
                
                logger.info(f"Generated API token '{name}' (ID: {token_id}) by user {cherrypy.request.user['username']}")
                
                return {
                    'success': True,
                    'token': plaintext_token,
                    'token_id': token_id,
                    'name': name,
                    'warning': 'Save this token securely - it will not be shown again'
                }
            
            except Exception as e:
                logger.error(f"Token generation error: {e}")
                cherrypy.response.status = 500
                return {
                    'success': False,
                    'error': 'Failed to generate token'
                }
        else:
            raise cherrypy.HTTPError(405, "Method not allowed")
    
    @cherrypy.expose
    @cherrypy.tools.json_out()
    @require_auth
    def default(self, token_id=None):
        # Handle CORS preflight
        if cherrypy.request.method == 'OPTIONS':
            return {}
        
        # Get token manager from cherrypy config
        token_manager = cherrypy.config.get('token_manager')
        if not token_manager:
            cherrypy.response.status = 500
            return {'success': False, 'error': 'Token manager not available'}
        
        if cherrypy.request.method == 'DELETE':
            try:
                if not token_id:
                    cherrypy.response.status = 400
                    return {
                        'success': False,
                        'error': 'Token ID is required'
                    }
                
                # Convert to int
                try:
                    token_id_int = int(token_id)
                except ValueError:
                    cherrypy.response.status = 400
                    return {
                        'success': False,
                        'error': 'Invalid token ID'
                    }
                
                # Revoke the token
                success = token_manager.revoke_token(token_id_int)
                
                if success:
                    logger.info(f"Revoked API token ID {token_id_int} by user {cherrypy.request.user['username']}")
                    return {
                        'success': True,
                        'message': 'Token revoked successfully'
                    }
                else:
                    cherrypy.response.status = 404
                    return {
                        'success': False,
                        'error': 'Token not found'
                    }
            
            except Exception as e:
                logger.error(f"Token revocation error: {e}")
                cherrypy.response.status = 500
                return {
                    'success': False,
                    'error': 'Failed to revoke token'
                }
        else:
            raise cherrypy.HTTPError(405, "Method not allowed")


class AuthEndpoints:
    
    def __init__(self, config, jwt_handler, token_manager, config_manager=None):
        self.config = config
        self.jwt_handler = jwt_handler
        self.token_manager = token_manager
        self.config_manager = config_manager
    
    @cherrypy.expose
    def login(self, **kwargs):

        cherrypy.response.headers['Content-Type'] = 'application/json'
        
        # Handle CORS preflight
        if cherrypy.request.method == 'OPTIONS':
            cherrypy.response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
            cherrypy.response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-API-Key'
            return b''
        
        if cherrypy.request.method != 'POST':
            raise cherrypy.HTTPError(405, "Method not allowed")
        
        try:
            # Parse JSON body manually since we can't use json_in decorator with OPTIONS
            import json
            body = cherrypy.request.body.read().decode('utf-8')
            data = json.loads(body) if body else {}
            
            username = data.get('username', '').strip()
            password = data.get('password', '')
            client_id = data.get('client_id', '').strip()
            
            if not username or not password or not client_id:
                return json.dumps({
                    'success': False,
                    'error': 'Missing required fields: username, password, client_id'
                }).encode('utf-8')
            
            # Validate credentials against config
            # Check if username is 'admin' and password matches config
            repeater_config = self.config.get('repeater', {})
            security_config = repeater_config.get('security', {})
            config_password = security_config.get('admin_password', '')
            
            # Don't allow login with empty or unconfigured password
            if not config_password:
                logger.warning(f"Login attempt rejected - password not configured")
                return json.dumps({
                    'success': False,
                    'error': 'System not configured. Please complete setup wizard.'
                }).encode('utf-8')
            
            if username == 'admin' and password == config_password:
                # Create JWT token
                token = self.jwt_handler.create_jwt(username, client_id)
                
                logger.info(f"Successful login for user '{username}' from client '{client_id[:8]}...'")
                
                return json.dumps({
                    'success': True,
                    'token': token,
                    'expires_in': self.jwt_handler.expiry_minutes * 60,
                    'username': username
                }).encode('utf-8')
            else:
                logger.warning(f"Failed login attempt for user '{username}'")
                
                # Don't reveal which part was wrong
                return json.dumps({
                    'success': False,
                    'error': 'Invalid username or password'
                }).encode('utf-8')
        
        except Exception as e:
            logger.error(f"Login error: {e}")
            return json.dumps({
                'success': False,
                'error': 'Internal server error'
            }).encode('utf-8')
    
    @cherrypy.expose
    @cherrypy.tools.json_out()
    @require_auth
    def verify(self):
        if cherrypy.request.method != 'GET':
            raise cherrypy.HTTPError(405, "Method not allowed")
        
        return {
            'success': True,
            'authenticated': True,
            'user': cherrypy.request.user
        }
    
    @cherrypy.expose
    def refresh(self, **kwargs):

        cherrypy.response.headers['Content-Type'] = 'application/json'
        
        # Handle CORS preflight
        if cherrypy.request.method == 'OPTIONS':
            cherrypy.response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
            cherrypy.response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-API-Key'
            return b''
        
        if cherrypy.request.method != 'POST':
            raise cherrypy.HTTPError(405, "Method not allowed")
        
        try:
            import json
            
            # Manual authentication check (can't use @require_auth since we need to handle OPTIONS)
            auth_header = cherrypy.request.headers.get('Authorization', '')
            api_key = cherrypy.request.headers.get('X-API-Key', '')
            
            jwt_handler = cherrypy.config.get('jwt_handler')
            token_manager = cherrypy.config.get('token_manager')
            
            user_info = None
            
            # Check JWT first
            if auth_header.startswith('Bearer '):
                token = auth_header[7:]
                payload = jwt_handler.verify_jwt(token)
                if payload:
                    user_info = {
                        'username': payload['sub'],
                        'client_id': payload.get('client_id'),
                        'auth_method': 'jwt'
                    }
            
            # Check API token
            if not user_info and api_key:
                token_data = token_manager.verify_token(api_key)
                if token_data:
                    user_info = {
                        'username': 'admin',
                        'token_id': token_data['id'],
                        'auth_method': 'api_token'
                    }
            
            if not user_info:
                return json.dumps({
                    'success': False,
                    'error': 'Unauthorized - Valid JWT or API token required'
                }).encode('utf-8')
            
            # Parse request body
            body = cherrypy.request.body.read().decode('utf-8')
            data = json.loads(body) if body else {}
            
            client_id = data.get('client_id', user_info.get('client_id', '')).strip()
            
            if not client_id:
                return json.dumps({
                    'success': False,
                    'error': 'Client ID is required'
                }).encode('utf-8')
            
            # Create new JWT token (refreshes expiry time)
            new_token = self.jwt_handler.create_jwt(user_info['username'], client_id)
            
            logger.info(f"Token refreshed for user '{user_info['username']}' from client '{client_id[:8]}...'")
            
            return json.dumps({
                'success': True,
                'token': new_token,
                'expires_in': self.jwt_handler.expiry_minutes * 60,
                'username': user_info['username']
            }).encode('utf-8')
        
        except Exception as e:
            logger.error(f"Token refresh error: {e}")
            return json.dumps({
                'success': False,
                'error': 'Failed to refresh token'
            }).encode('utf-8')
    
    @cherrypy.expose
    def change_password(self):

        import json
        
        cherrypy.response.headers['Content-Type'] = 'application/json'
        
        # Handle CORS preflight
        if cherrypy.request.method == 'OPTIONS':
            cherrypy.response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
            cherrypy.response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-API-Key'
            return b''
        
        if cherrypy.request.method != 'POST':
            raise cherrypy.HTTPError(405, "Method not allowed")
        
        # Require authentication for POST
        # Get auth handlers from global cherrypy config
        jwt_handler = cherrypy.config.get('jwt_handler')
        token_manager = cherrypy.config.get('token_manager')
        
        if not jwt_handler or not token_manager:
            logger.error("Auth handlers not configured")
            raise cherrypy.HTTPError(500, "Authentication not configured")
        
        # Try JWT authentication first
        auth_header = cherrypy.request.headers.get('Authorization', '')
        user = None
        
        if auth_header.startswith('Bearer '):
            token = auth_header[7:]  # Remove 'Bearer ' prefix
            payload = jwt_handler.verify_jwt(token)
            
            if payload:
                user = {
                    'username': payload['sub'],
                    'client_id': payload['client_id'],
                    'auth_type': 'jwt'
                }
        
        # Try API token authentication if JWT failed
        if not user:
            api_key = cherrypy.request.headers.get('X-API-Key', '')
            if api_key:
                token_info = token_manager.verify_token(api_key)
                
                if token_info:
                    user = {
                        'username': 'api_token',
                        'token_name': token_info['name'],
                        'token_id': token_info['id'],
                        'auth_type': 'api_token'
                    }
        
        if not user:
            cherrypy.response.status = 401
            return json.dumps({
                'success': False,
                'error': 'Unauthorized - Valid JWT or API token required'
            }).encode('utf-8')
        
        try:
            # Parse JSON body manually
            body = cherrypy.request.body.read().decode('utf-8')
            data = json.loads(body) if body else {}
            
            current_password = data.get('current_password', '')
            new_password = data.get('new_password', '')
            
            if not current_password or not new_password:
                cherrypy.response.status = 400
                return json.dumps({
                    'success': False,
                    'error': 'Both current_password and new_password are required'
                }).encode('utf-8')
            
            # Validate new password strength
            if len(new_password) < 8:
                cherrypy.response.status = 400
                return json.dumps({
                    'success': False,
                    'error': 'New password must be at least 8 characters long'
                }).encode('utf-8')
            
            # Verify current password
            repeater_config = self.config.get('repeater', {})
            security_config = repeater_config.get('security', {})
            config_password = security_config.get('admin_password', '')
            
            if not config_password:
                cherrypy.response.status = 500
                return json.dumps({
                    'success': False,
                    'error': 'System configuration error'
                }).encode('utf-8')
            
            if current_password != config_password:
                cherrypy.response.status = 401
                return json.dumps({
                    'success': False,
                    'error': 'Current password is incorrect'
                }).encode('utf-8')
            
            # Update password in config
            if 'repeater' not in self.config:
                self.config['repeater'] = {}
            if 'security' not in self.config['repeater']:
                self.config['repeater']['security'] = {}
            
            self.config['repeater']['security']['admin_password'] = new_password
            
            # Save to config file using ConfigManager
            if self.config_manager:
                if self.config_manager.save_to_file():
                    logger.info(f"Admin password changed successfully by user {user['username']}")
                    return json.dumps({
                        'success': True,
                        'message': 'Password changed successfully. Please log in again with your new password.'
                    }).encode('utf-8')
                else:
                    cherrypy.response.status = 500
                    return json.dumps({
                        'success': False,
                        'error': 'Failed to save password to config file'
                    }).encode('utf-8')
            else:
                cherrypy.response.status = 500
                return json.dumps({
                    'success': False,
                    'error': 'Config manager not available'
                }).encode('utf-8')
        
        except Exception as e:
            logger.error(f"Password change error: {e}")
            cherrypy.response.status = 500
            return json.dumps({
                'success': False,
                'error': 'Failed to change password'
            }).encode('utf-8')