import sys
import unittest

sys.path.append(r"C:\Users\Free user\Jarvis")
from core.ussd import USSDManager

class TestUSSDConfigurationAndPrefixes(unittest.TestCase):
    def setUp(self):
        # Initialize manager without executing ADB commands
        self.manager = USSDManager(adb_path="", device_id="")

    def test_sim1_prefix_resolution(self):
        # +251954531474 -> Ethio Telecom, *804#
        details = self.manager.get_sim_details("SIM1")
        self.assertEqual(details["phone_number"], "+251954531474")
        self.assertEqual(details["network"], "Ethio Telecom")
        self.assertEqual(details["ussd_code"], "*804#")
        self.assertEqual(details["sub_id"], 2)

    def test_sim2_prefix_resolution(self):
        # +251998065377 -> Ethio Telecom, *804# (since it starts with +2519)
        details = self.manager.get_sim_details("SIM2")
        self.assertEqual(details["phone_number"], "+251998065377")
        self.assertEqual(details["network"], "Ethio Telecom")
        self.assertEqual(details["ussd_code"], "*804#")
        self.assertEqual(details["sub_id"], 5)

    def test_safaricom_prefix_resolution(self):
        # Test number starting with +2517 -> Safaricom Ethiopia, *704#
        net, ussd = self.manager.identify_network("+251711223344")
        self.assertEqual(net, "Safaricom Ethiopia")
        self.assertEqual(ussd, "*704#")

    def test_manual_override(self):
        # Test manual override feature in config
        self.manager.config["sims"]["SIM1"]["manual_override"] = {
            "network": "Custom Operator",
            "ussd_code": "*999#"
        }
        details = self.manager.get_sim_details("SIM1")
        self.assertEqual(details["network"], "Custom Operator")
        self.assertEqual(details["ussd_code"], "*999#")

if __name__ == "__main__":
    unittest.main()
