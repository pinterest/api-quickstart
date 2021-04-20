from api_object import ApiObject

class Pin(ApiObject):
    def __init__(self, pin_id, api_config, access_token):
        super().__init__(api_config, access_token)
        self.pin_id = pin_id

    def get(self):
        return self.request_data('/v3/pins/{}'.format(self.pin_id))

    @classmethod
    def print_summary(klass, pin_data):
        print('--- Pin Summary ---')
        print('Pin ID: ' + pin_data['id'])
        print('Description: ' + pin_data['description'])
        print('Domain: ' + pin_data['domain'])
        print('Native format type: ' + pin_data['native_format_type'])
        print('--------------------')

    def create(self, pin_data, board_id, section=None):
        # TODO: carousel_data_json
        OPTIONAL_ATTRIBUTES = [
            'alt_text',
            'description',
            'title',
        ]
        create_data = {
            'board_id': board_id,
            'image_url': pin_data['image_large_url']
        }
        if section:
            create_data['section'] = section
        link = pin_data.get('link')
        if link:
            create_data['source_url'] = link

        # TODO: finish reviewing all of the fields
        for key in OPTIONAL_ATTRIBUTES:
            value = pin_data.get(key)
            if value:
                create_data[key] = value

        return self.put_data('/v3/pins/', create_data)
