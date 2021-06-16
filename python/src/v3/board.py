from v3.api_object import ApiObject # specifying v3 required for unit tests

class Board(ApiObject):
    def __init__(self, board_id, api_config, access_token):
        super().__init__(api_config, access_token)
        self.board_id = board_id

    def get(self):
        if not self.board_id:
            raise ValueError('board_id must be set to get a board')
        return self.request_data(f'/v3/boards/{self.board_id}/')

    @classmethod
    def print_summary(klass, board_data):
        print('--- Board Summary ---')
        print(f"Board ID: {board_data['id']}")
        print(f"Name: {board_data['name']}")
        print(f"URL: {board_data['url']}")
        print(f"Category: {board_data['category']}")
        print(f"Description: {board_data.get('description')}")
        print(f"Pin Count: {board_data.get('pin_count')}")
        print('--------------------')

    def create(self, board_data):
        OPTIONAL_ATTRIBUTES = [
            'category',
            'collaborator_invites_enabled',
            'description',
            'event_date',
            'event_start_date',
            'initial_pin_client_tracking_params',
            'initial_pins',
            'layout',
            'privacy',
            'protected',
            'return_existing'
        ]
        create_data = {
            'name': board_data['name'],
        }
        for key in OPTIONAL_ATTRIBUTES:
            value = board_data.get(key)
            if value:
                create_data[key] = value

        new_board_data = self.put_data('/v3/boards/', create_data)
        self.board_id = new_board_data['id']
        return new_board_data

    def delete(self):
        self.delete_and_check(f'/v3/boards/{self.board_id}/')

    def get_pins(self):
        return self.get_iterator(f'/v3/boards/{self.board_id}/pins/')

    def get_sections(self):
        return self.get_iterator(f'/v3/board/{self.board_id}/sections/')

    @classmethod
    def print_section(klass, section_data):
        print('--- Board Section ---')
        print(f"Section ID: {section_data['id']}")
        print(f"Title: {section_data['title']}")
        print(f"Pin Count: {section_data['pin_count']}")
        print('---------------------')

    @classmethod
    def print_sections(klass, sections_iterator):
        for section in sections_iterator:
            self.print_section(section)

    def create_section(self, section_data):
        OPTIONAL_ATTRIBUTES = [
            'client_id',
            'initial_pins',
            'preselected_pins',
            'title_source'
        ]
        create_data = {
            'title': section_data['title'],
        }
        for key in OPTIONAL_ATTRIBUTES:
            value = section_data.get(key)
            if value:
                create_data[key] = value

        return self.put_data(f'/v3/board/{self.board_id}/sections/', create_data)

    def get_section_pins(self, section_id):
        return self.get_iterator(f'/v3/board/sections/{section_id}/pins/')
