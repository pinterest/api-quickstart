from api_object import ApiObject

class Board(ApiObject):
    def __init__(self, board_id, api_config, access_token):
        super().__init__(api_config, access_token)
        self.board_id = board_id

    def get(self):
        return self.request_data('/v3/boards/{}'.format(self.board_id))

    @classmethod
    def print_summary(klass, board_data):
        print('--- Board Summary ---')
        print('Board ID: ' + board_data['id'])
        print('Name: ' + board_data['name'])
        print('URL: ' + board_data['url'])
        print('Category: ' + str(board_data['category']))
        print(f"Description: {board_data.get('description')}")
        print('--------------------')
