from branch import freeze
from run import lab
base=lab.read(lab.HERE/'configs/h2-a-light-for-others.json')
original=lab.read(lab.OUT/'h1-lantern-harbour/config.json')
phrases=[p for p in original['phrases'] if p['start']<=7.5]
phrases.extend([dict(start=7.5,duration=10,zoom=.55,turn=-12,travel=[.10,-.05],center=[.35,.65],radius=3.5),dict(start=12,duration=10,zoom=.05,turn=17,travel=[-.1,0],center=[.7,.5],radius=3),dict(kind='wave',start=12,duration=11,amplitude=.032,wavelength=1.5,cycles=.6)])
freeze('h1-lantern-harbour','h3-follow-the-beacon',180,18,[p for p in base['prompt_schedule'] if p['at']>7.5],[p for p in base['noise_schedule'] if p['at']>7.5],phrases)
