import DateTimeModelElement
import DecimalIntegerValueModelElement
import DelimitedDataModelElement
import FixedDataModelElement
import IpAddressDataModelElement
import SequenceModelElement
import VariableByteDataModelElement
import WhiteSpaceLimitedDataModelElement

"""This function defines how to parse an AHIT Apache webserver 
log line part after found after any standard logging preamble, 
e.g. from syslog."""
def getModel():
  model=SequenceModelElement.SequenceModelElement('apache', [FixedDataModelElement.FixedDataModelElement('sname', 'apache: '),
      DecimalIntegerValueModelElement.DecimalIntegerValueModelElement('pid'),
      FixedDataModelElement.FixedDataModelElement('s0', ' '),
      IpAddressDataModelElement.IpAddressDataModelElement('hostip'),
      FixedDataModelElement.FixedDataModelElement('s1', ':'),
      DecimalIntegerValueModelElement.DecimalIntegerValueModelElement('hostport'),
      FixedDataModelElement.FixedDataModelElement('s2', ' "'),
      VariableByteDataModelElement.VariableByteDataModelElement('sname', '-.01234567890abcdefghijklmnopqrstuvwxyz'),
      FixedDataModelElement.FixedDataModelElement('s3', '" "'),
      VariableByteDataModelElement.VariableByteDataModelElement('cname', '-.01234567890abcdefghijklmnopqrstuvwxyz'),
      FixedDataModelElement.FixedDataModelElement('s4', '" '),
      IpAddressDataModelElement.IpAddressDataModelElement('remoteip'),
      FixedDataModelElement.FixedDataModelElement('s5', ' - - ['),
      DateTimeModelElement.DateTimeModelElement('time', '%d/%b/%Y:%H:%M:%S', 20, True),
      FixedDataModelElement.FixedDataModelElement('s5', ' +0000] "'),
      WhiteSpaceLimitedDataModelElement.WhiteSpaceLimitedDataModelElement('method'),
      FixedDataModelElement.FixedDataModelElement('s6', ' '),
      WhiteSpaceLimitedDataModelElement.WhiteSpaceLimitedDataModelElement('url'),
      FixedDataModelElement.FixedDataModelElement('s7', ' '),
      VariableByteDataModelElement.VariableByteDataModelElement('httpver', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789/.'),
      FixedDataModelElement.FixedDataModelElement('s8', '" '),
      DecimalIntegerValueModelElement.DecimalIntegerValueModelElement('status'),
      FixedDataModelElement.FixedDataModelElement('s9', ' '),
      DecimalIntegerValueModelElement.DecimalIntegerValueModelElement('length'),
      FixedDataModelElement.FixedDataModelElement('s9', ' "'),
      DelimitedDataModelElement.DelimitedDataModelElement('referer', '"'),
      FixedDataModelElement.FixedDataModelElement('s10', '" "'),
      DelimitedDataModelElement.DelimitedDataModelElement('agent', '"'),
      FixedDataModelElement.FixedDataModelElement('s11', '"'),
])
  return(model)
