import logging
from admin_app.app import App as BaseWSApp
from admin_app.exc import BaseError, FieldRequiredError

logger = logging.getLogger()


class AuthError(BaseError):
    code = 100
    message = "Auth Error"


class AuthRequired(AuthError):

    message = 'Auth Required'
    code = 100


class Auth:

    name = 'auth'

    def handlers(self):
        return {
            'auth.login': self.h_login,
            'auth.logout': self.h_logout,
            'auth.list_users': self.h_list_users,
        }

    def get_user(self, env, required=False):
        user = getattr(env, 'user', None)
        if (not user) and required:
            raise AuthRequired
        else:
            return user

    def set_user(self, env, user):
        env.user = user

    async def h_login(self, env, message):
        user = message.get('user')
        if not user:
            raise FieldRequiredError('user')

        for client in env.app.clients:
            client_user = self.get_user(client)
            if user==client_user:
                raise AuthError('User already "{}" authorized'.format(user))
        self.set_user(env, user)
        await env.send('auth.login', {'user': user})
        await env.send_to_all('auth.login_notification', {'user': user})

    async def h_logout(self, env, message):
        user = self.get_user(env, required=True)
        self.set_user(env, None)
        await env.send('auth.login', {'user': user})
        await env.send_to_all('auth.logout_notification', {'user': user})

    async def h_list_users(self, env, message):
        users = []
        for client in env.app.clients:
            user = env.app.auth.get_user(client)
            if user:
                users.append(user)
        await env.send('auth.list_users', {'users': users})


class Chat:

    name = 'chat'

    def handlers(self):
        return {
            'chat.send': self.h_send,
        }

    async def h_send(self, env, message):
        user = env.app.auth.get_user(env, required=True)
        message = message.get('message')
        if not message:
            raise FieldRequiredError('message')
        await env.send_to_all('chat.send_notification', {
            'user': user,
            'message': message,
        })


class Fields:

    field_names = ['field1', 'field2', 'field3', 'field4', 'field5']
    field_values = {
        'field1': 'Иванов Иван Иванович',
        'field2': 'Иванов Иван Иванович',
        'field3': 'Иванов Иван Иванович',
        'field4': 'Иванов Иван Иванович',
        'field5': 'Иванов Иван Иванович',
    }

    def handlers(self):
        return {
            'fields.list': self.h_list,
            'fields.block': self.h_block,
            'fields.unblock': self.h_unblock,
            'fields.change': self.h_change,
        }

    async def h_list(self, env, message):
        result = []
        blocks = self.get_blocks(env)
        for name in self.field_names:
            result.append({
                'name': name,
                'value': self.field_values[name],
                'block': blocks.get(name),
            })
        await env.send('fields.list', {'fields': result})

    async def h_block(self, env, message):
        user = env.app.auth.get_user(env, required=True)
        name = message.get('name')
        blocks = self.get_blocks(env)
        block_user = blocks.get(name)
        if block_user and block_user!=user:
            raise BaseError('Block failure')
        else:
            env.block = name
            await env.send_to_all('fields.block_notification', {
                'name': name,
                'user': user,
                'value': self.field_values[name],
            })

    async def h_unblock(self, env, message):
        user = env.app.auth.get_user(env, required=True)
        name = message.get('name')
        blocks = self.get_blocks(env)
        block_user = blocks.get(name)

        if block_user and block_user!=user:
            raise BlockError('Unblock failure')
        else:
            env.block = None
            await env.send_to_all('fields.unblock_notification', {
                'name': name,
                'user': user,
                'value': self.field_values[name],
            })

    async def h_change(self, env, message):
        user = env.app.auth.get_user(env, required=True)
        name = message.get('name')
        value = message.get('value')
        if env.block!=name:
            raise BlockError('Block error')
        self.field_values[name] = value
        await env.send_to_all('fields.change_notification', {
            'name': name,
            'user': user,
            'value': value,
        })

    def get_blocks(self, env):
        blocks = {}
        for client in env.app.clients:
            user = env.app.auth.get_user(client)
            block = getattr(client, 'block', None)
            if user and block:
                blocks[block] = user
        return blocks


class WS_App(BaseWSApp):

    handlers = {}

    auth = Auth()
    handlers.update(auth.handlers())

    chat = Chat()
    handlers.update(chat.handlers())

    fields = Fields()
    handlers.update(fields.handlers())
