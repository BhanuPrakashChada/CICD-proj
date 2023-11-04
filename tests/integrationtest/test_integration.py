import unittest
from unittest.mock import patch
from flask_testing import TestCase
from app import app, get_system_info, plot_system_info

class TestAppIntegration(TestCase):

    def create_app(self):
        app.config['TESTING'] = True
        return app

    @patch('app.get_system_info')
    @patch('app.plot_system_info')
    def test_index_page(self, mock_plot_system_info, mock_get_system_info):
        
        mock_get_system_info.return_value = (50.0, 60.0, {'percent': 70.0, 'power_plugged': True}, [{'name': 'test_process', 'cpu_percent': 30.0}])

        
        mock_plot_system_info.return_value = ('<div id="mock_cpu_plot">Mock CPU Plot</div>',
                                              '<div id="mock_memory_plot">Mock Memory Plot</div>',
                                              '<div id="mock_battery_plot">Mock Battery Plot</div>',
                                              '<div id="mock_process_plot">Mock Process Plot</div>')

        response = self.client.get('/')

        
        self.assert200(response)
        self.assertIn(b'Mock CPU Plot', response.data)
        self.assertIn(b'Mock Memory Plot', response.data)
        self.assertIn(b'Mock Battery Plot', response.data)
        self.assertIn(b'Mock Process Plot', response.data)

if __name__ == '__main__':
    unittest.main()
