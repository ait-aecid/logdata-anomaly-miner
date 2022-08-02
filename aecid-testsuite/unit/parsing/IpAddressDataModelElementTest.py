import unittest
from aminer.parsing.IpAddressDataModelElement import IpAddressDataModelElement
from aminer.parsing.MatchContext import MatchContext
from aminer.parsing.MatchElement import MatchElement
from unit.TestBase import TestBase, DummyMatchContext


class IpAddressDataModelElementTest(TestBase):
    """Unittests for the IpAddressDataModelElement."""

    id_ = "ip"
    path = "path"

    def test1get_match_element_valid_ipv4_match(self):
        """
        This test case checks the functionality by parsing a real IP-addresses.
        The boundary values for IP-addresses is 0.0.0.0 - 255.255.255.255
        The numerical representation of the ip address was calculated with the help of http://www.aboutmyip.com/AboutMyXApp/IP2Integer.jsp.
        """
        ip_addr_dme = IpAddressDataModelElement(self.id_)
        data = b"192.168.0.155 followed by some text"
        value = b"192.168.0.155"
        match_context = DummyMatchContext(data)
        match_element = ip_addr_dme.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, value, 3232235675, None)

        data = b"0.0.0.0."
        value = b"0.0.0.0"
        match_context = DummyMatchContext(data)
        match_element = ip_addr_dme.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, value, 0, None)

        data = b"255.255.255.255."
        value = b"255.255.255.255"
        match_context = DummyMatchContext(data)
        match_element = ip_addr_dme.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, value, 4294967295, None)

        data = b"192.168.0.155.22 followed by some text"
        value = b"192.168.0.155"
        match_context = DummyMatchContext(data)
        match_element = ip_addr_dme.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, value, 3232235675, None)

    def test2get_match_element_no_match_ipv4(self):
        """
        Test if wrong formats are determined and boundary values are checked.
        Also check if hexadecimal ip addresses are not parsed as these are not allowed.
        Test if ip addresses are found, even if they are followed by other numbers.
        """
        ip_addr_dme = IpAddressDataModelElement(self.id_)
        data = b"192. 168.0.155 followed by some text"
        match_context = DummyMatchContext(data)
        match_element = ip_addr_dme.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

        data = b"256.168.0.155 followed by some text"
        match_context = DummyMatchContext(data)
        match_element = ip_addr_dme.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

        data = b"\xc0\xa8\x00\x9b"
        match_context = DummyMatchContext(data)
        match_element = ip_addr_dme.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

    def test3get_match_element_valid_ipv6_match(self):
        """
        This test case checks the functionality by parsing a real IP-addresses.
        The numerical representation of the ip address was calculated with the help of https://www.ipaddressguide.com/ipv6-to-decimal.
        """
        ip_addr_dme = IpAddressDataModelElement(self.id_, True)
        data = b"2001:4860:4860::8888 followed by some text"
        value = b"2001:4860:4860::8888"
        number = 42541956123769884636017138956568135816
        match_context = DummyMatchContext(data)
        match_element = ip_addr_dme.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, value, number, None)

        # full form of IPv6
        data = b"fe80:0000:0000:0000:0204:61ff:fe9d:f156."
        value = b"fe80:0000:0000:0000:0204:61ff:fe9d:f156"
        number = 338288524927261089654164245681446711638
        match_context = DummyMatchContext(data)
        match_element = ip_addr_dme.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, value, number, None)

        # drop leading zeroes
        data = b"fe80:0:0:0:204:61ff:fe9d:f156."
        value = b"fe80:0:0:0:204:61ff:fe9d:f156"
        match_context = DummyMatchContext(data)
        match_element = ip_addr_dme.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, value, number, None)

        # collapse multiple zeroes to :: in the IPv6 address
        data = b"fe80::204:61ff:fe9d:f156 followed by some text"
        value = b"fe80::204:61ff:fe9d:f156"
        match_context = DummyMatchContext(data)
        match_element = ip_addr_dme.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, value, number, None)

        # localhost
        data = b"::1 followed by some text"
        value = b"::1"
        number = 1
        match_context = DummyMatchContext(data)
        match_element = ip_addr_dme.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, value, number, None)

        # link-local prefix
        data = b"fe80:: followed by some text"
        value = b"fe80::"
        number = 338288524927261089654018896841347694592
        match_context = DummyMatchContext(data)
        match_element = ip_addr_dme.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, value, number, None)

        # global unicast prefix
        data = b"2001:: followed by some text"
        value = b"2001::"
        number = 42540488161975842760550356425300246528
        match_context = DummyMatchContext(data)
        match_element = ip_addr_dme.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, value, number, None)

    def test4get_match_element_no_match_ipv6(self):
        """Test if wrong formats are determined and boundary values are checked."""
        ip_addr_dme = IpAddressDataModelElement(self.id_, True)
        # IPv4 dotted quad at the end
        data = b"fe80:0000:0000:0000:0204:61ff:254.157.241.86"
        match_context = DummyMatchContext(data)
        match_element = ip_addr_dme.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

        # drop leading zeroes, IPv4 dotted quad at the end
        data = b"fe80:0:0:0:0204:61ff:254.157.241.86"
        match_context = DummyMatchContext(data)
        match_element = ip_addr_dme.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

        # dotted quad at the end, multiple zeroes collapsed
        data = b"fe80::204:61ff:254.157.241.86"
        match_context = DummyMatchContext(data)
        match_element = ip_addr_dme.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

        # multiple :: in the IPv6 address
        data = b"fe80::204:61ff::fe9d:f156"
        match_context = DummyMatchContext(data)
        match_element = ip_addr_dme.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

        # IPv4 address with ipv6 being True
        data = b"254.157.241.86"
        match_context = DummyMatchContext(data)
        match_element = ip_addr_dme.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

        # g in ip address
        data = b"2001:4860:48g0::8888 followed by some text"
        match_context = DummyMatchContext(data)
        match_element = ip_addr_dme.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

    def test5element_id_input_validation(self):
        """Check if element_id is validated."""
        self.assertRaises(ValueError, IpAddressDataModelElement, "")  # empty element_id
        self.assertRaises(TypeError, IpAddressDataModelElement, None)  # None element_id
        self.assertRaises(TypeError, IpAddressDataModelElement, b"path")  # bytes element_id is not allowed
        self.assertRaises(TypeError, IpAddressDataModelElement, True)  # boolean element_id is not allowed
        self.assertRaises(TypeError, IpAddressDataModelElement, 123)  # integer element_id is not allowed
        self.assertRaises(TypeError, IpAddressDataModelElement, 123.22)  # float element_id is not allowed
        self.assertRaises(TypeError, IpAddressDataModelElement, {"id": "path"})  # dict element_id is not allowed
        self.assertRaises(TypeError, IpAddressDataModelElement, ["path"])  # list element_id is not allowed
        self.assertRaises(TypeError, IpAddressDataModelElement, [])  # empty list element_id is not allowed
        self.assertRaises(TypeError, IpAddressDataModelElement, ())  # empty tuple element_id is not allowed
        self.assertRaises(TypeError, IpAddressDataModelElement, set())  # empty set element_id is not allowed

    def test6ipv6_input_validation(self):
        """Check if ipv6 is validated."""
        self.assertRaises(TypeError, IpAddressDataModelElement, self.id_, "path")  # string ipv6
        self.assertRaises(TypeError, IpAddressDataModelElement, self.id_, None)  # None ipv6
        self.assertRaises(TypeError, IpAddressDataModelElement, self.id_, b"path")  # bytes ipv6 is not allowed
        self.assertRaises(TypeError, IpAddressDataModelElement, self.id_, 123)  # integer ipv6 is not allowed
        self.assertRaises(TypeError, IpAddressDataModelElement, self.id_, 123.22)  # float ipv6 is not allowed
        self.assertRaises(TypeError, IpAddressDataModelElement, self.id_, {"id": "path"})  # dict ipv6 is not allowed
        self.assertRaises(TypeError, IpAddressDataModelElement, self.id_, ["path"])  # list ipv6 is not allowed
        self.assertRaises(TypeError, IpAddressDataModelElement, self.id_, [])  # empty list ipv6 is not allowed
        self.assertRaises(TypeError, IpAddressDataModelElement, self.id_, ())  # empty tuple ipv6 is not allowed
        self.assertRaises(TypeError, IpAddressDataModelElement, self.id_, set())  # empty set ipv6 is not allowed

    def test7get_match_element_match_context_input_validation(self):
        """Check if an exception is raised, when other classes than MatchContext are used in get_match_element."""
        model_element = IpAddressDataModelElement(self.id_)
        data = b"abcdefghijklmnopqrstuvwxyz.!?"
        model_element.get_match_element(self.path, DummyMatchContext(data))
        model_element.get_match_element(self.path, MatchContext(data))

        self.assertRaises(AttributeError, model_element.get_match_element, self.path, MatchElement(None, data, None, None))
        self.assertRaises(AttributeError, model_element.get_match_element, self.path, data)
        self.assertRaises(AttributeError, model_element.get_match_element, self.path, data.decode())
        self.assertRaises(AttributeError, model_element.get_match_element, self.path, 123)
        self.assertRaises(AttributeError, model_element.get_match_element, self.path, 123.22)
        self.assertRaises(AttributeError, model_element.get_match_element, self.path, True)
        self.assertRaises(AttributeError, model_element.get_match_element, self.path, None)
        self.assertRaises(AttributeError, model_element.get_match_element, self.path, [])
        self.assertRaises(AttributeError, model_element.get_match_element, self.path, {"key": MatchContext(data)})
        self.assertRaises(AttributeError, model_element.get_match_element, self.path, set())
        self.assertRaises(AttributeError, model_element.get_match_element, self.path, ())
        self.assertRaises(AttributeError, model_element.get_match_element, self.path, model_element)

    def test8performance(self):  # skipcq: PYL-R0201
        """Test the performance of the implementation."""
        import_setup = """
import copy
from unit.TestBase import DummyMatchContext
from aminer.parsing.IpAddressDataModelElement import IpAddressDataModelElement
times = 300000
"""
        ip_192_setup = """
ip = b"192.168.0.155"
dme = IpAddressDataModelElement("s0")
"""
        ip_0_setup = """
ip = b"0.0.0.0"
dme = IpAddressDataModelElement("s0")
"""
        ip_255_setup = """
ip = b"255.255.255.255"
dme = IpAddressDataModelElement("s0")
"""
        end_setup = """
dummy_match_context = DummyMatchContext(ip)
dummy_match_context_list = [copy.deepcopy(dummy_match_context) for _ in range(times)]

def run():
    match_context = dummy_match_context_list.pop(0)
    dme.get_match_element("match", match_context)
"""
        _setup192 = import_setup + ip_192_setup + end_setup
        _setup0 = import_setup + ip_0_setup + end_setup
        _setup255 = import_setup + ip_255_setup + end_setup
        # import timeit
        # times = 300000
        # print()
        # print("192.168.0.155 is run 300.000 times.")
        # t = timeit.timeit(setup=_setup192, stmt="run()", number=times)
        # print("time: ", t)
        # print()
        # print("0.0.0.0 is run 300.000 times.")
        # t = timeit.timeit(setup=_setup0, stmt="run()", number=times)
        # print("time: ", t)
        # print()
        # print("255.255.255.255 is run 300.000 times.")
        # t = timeit.timeit(setup=_setup255, stmt="run()", number=times)
        # print("time: ", t)


if __name__ == "__main__":
    unittest.main()
