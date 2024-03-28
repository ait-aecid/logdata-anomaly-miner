cp demo/aminerXmlInputDemo/xml-input-demo-config.yml /tmp/xml-input-demo-config.yml
sudo chown -R aminer:aminer /tmp/lib 2> /dev/null
sudo chmod +x demo/aminerXmlInputDemo/aminerXmlInputDemo.sh
sudo ./demo/aminerXmlInputDemo/aminerXmlInputDemo.sh > /tmp/out.txt
exit_code=$?

OUTPUT=$(cat /tmp/out.txt)

read -r -d '' VAR << END
New path(es) detected
NewMatchPathDetector: "DefaultNewMatchPathDetector" (1 lines)
  /model: {'messages': [{'note': {'+id': '501', 'to': 'Tove', 'from': 'Jani', 'heading': None, 'body': {'text1': "Don't forget me this weekend!", 'text2': "Don't forget me this weekend!"}}}, {'note': {'+id': '502', '+opt': 'text', 'to': 'Jani', 'from': 'Tove', 'heading': 'Re: ', 'body': {'text1': 'I will not', 'text2': 'I will not'}}}]}
  /model/messages/note/+id/id: 501
  /model/messages/note/to/to: Tove
  /model/messages/note/from/from: Jani
  /model/messages/note/?heading: null
  /model/messages/note/body/text1/text1: Don't forget me this weekend!
  /model/messages/note/body/text2/text2: Don't forget me this weekend!
  /model/messages/note/+id/id: 502
  /model/messages/note/_+opt/opt: text
  /model/messages/note/to/to: Jani
  /model/messages/note/from/from: Tove
  /model/messages/note/?heading/heading: Re:
  /model/messages/note/body/text1/text1: I will not
  /model/messages/note/body/text2/text2: I will not
['/model', '/model/messages/note/+id/id', '/model/messages/note/to/to', '/model/messages/note/from/from', '/model/messages/note/body/text1/text1', '/model/messages/note/body/text2/text2', '/model/messages/note/+id/id/0', '/model/messages/note/to/to/0', '/model/messages/note/from/from/0', '/model/messages/note/?heading', '/model/messages/note/body/text1/text1/0', '/model/messages/note/body/text2/text2/0', '/model/messages/note/+id/id/1', '/model/messages/note/_+opt/opt', '/model/messages/note/to/to/1', '/model/messages/note/from/from/1', '/model/messages/note/?heading/heading', '/model/messages/note/body/text1/text1/1', '/model/messages/note/body/text2/text2/1']
Original log line: <?xml version="1.0" encoding="UTF-8"?>
<messages>
    <note id="501">
        <to>Tove</to>
        <from>Jani</from>
        <heading/>
        <body>
            <text1>Don't forget me this weekend!</text1>
            <text2>Don't forget me this weekend!</text2>
        </body>
    </note>
    <note id="502" opt="text">
        <to>Jani</to>
        <from>Tove</from>
        <heading>Re: </heading>
        <body>
            <text1>I will not</text1>
            <text2>I will not</text2>
        </body>
    </note>
</messages>
END
if [[ "$OUTPUT" != *"$VAR"* ]]; then
  echo "$VAR"
  echo
  echo "$OUTPUT"
  exit_code=1
fi

sudo rm /tmp/xml-input-demo-config.yml 2> /dev/null
sudo rm /tmp/syslog
sudo rm /tmp/out.txt
exit $exit_code
