import json

s = "Team members are : "
team_members = "{'result': [['Rishabh Tripathi'], ['Pavithra Badrinaaraayanan'], ['Ashwini Gupta'], ['Vivek Pandey'], ['Jay Prakash'], ['Karthik Ravivarapu'], ['Hari Krishna Singireddi']]}"
tm = json.loads(team_members)
print(tm)
for name in tm:
    s = s + str(tm[name])
print(s)