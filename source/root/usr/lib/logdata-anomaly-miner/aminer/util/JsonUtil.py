"""This module converts json strings to object structures
also supporting byte array structures."""
import json

from aminer.util import encodeByteStringAsString, decodeStringAsByteString

def dumpAsJson(inputObject):
  """Dump an input object encoded as string"""
  return json.dumps(encodeObject(inputObject))

def loadJson(inputString):
  """Load an string encoded as object structure"""
  return decodeObject(json.loads(inputString))

def encodeObject(term):
  """@param encodedObject return an object encoded as string"""
  encodedObject = ''
  if isinstance(term, str):
    encodedObject = 'string:' + term
  elif isinstance(term, bytes):
    encodedObject = 'bytes:' + encodeByteStringAsString(term)
  elif isinstance(term, (list, tuple)):
    encodedObject = [encodeObject(item) for item in term]
  elif isinstance(term, dict):
    encodedObject = {}
    for key, var in term.items():
      key = encodeObject(key)
      var = encodeObject(var)
      encodedObject[key] = var
  elif isinstance(term, (bool, int, float)) or term is None:
    encodedObject = term
  else:
    raise Exception('Unencodeable object %s' % type(term))

  return encodedObject

def decodeObject(term):
  """@param decodedObject return a string decoded as object structure"""
  decodedObject = ''
  if isinstance(term, str) and term.startswith('string:'):
    decodedObject = term[7:]
  elif isinstance(term, str) and term.startswith('bytes:'):
    decodedObject = term[6:]
    decodedObject = decodeStringAsByteString(decodedObject)
  elif isinstance(term, list):
    decodedObject = [decodeObject(item) for item in term]
  elif isinstance(term, dict):
    decodedObject = {}
    for key, var in term.items():
      key = decodeObject(key)
      var = decodeObject(var)
      decodedObject[key] = var
  else:
    decodedObject = term
  return decodedObject
