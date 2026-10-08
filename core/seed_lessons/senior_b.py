"""Senior Phase (part B): Term 1, Week 1 demo lessons, 2026.

Offerings (16):
    Grades 7, 8, 9 x SOC-SCI (Social Sciences), TECH (Technology),
    EMS (Economic and Management Sciences), CREATIVE-ARTS (Creative Arts),
    LO (Life Orientation); plus (7, 'CODING') (Coding and Robotics, Grade 7).

Sources used (Term 1, first topic of the year):
    * CAPS Social Sciences Senior Phase (Gr 7-9) and the DBE Social Sciences ATPs:
      Geography opens Term 1 with map skills (Gr 7 Map skills; Gr 8 Maps and globes;
      Gr 9 Map skills: contours, orthophoto and 1:50 000 topographic maps).
    * CAPS Technology Senior Phase and ATPs: Term 1 = Structures (with the design process).
    * CAPS EMS Senior Phase and ATPs: Gr 7 The economy - history of money;
      Gr 8 The economy - government; Gr 9 The economy - economic systems.
    * CAPS Creative Arts Senior Phase: Visual Arts, Create in 2D (elements of art,
      colour, design principles and drawing).
    * CAPS Life Orientation Senior Phase and ATPs: Development of the self in society -
      Gr 7 self-image; Gr 8 self-concept formation and self-motivation;
      Gr 9 goal-setting skills: personal lifestyle choices.
    * Coding and Robotics Grade 7 (DBE draft curriculum): Algorithms and coding -
      algorithms, flowcharts and block-based coding.
"""

LESSONS = {
    # ------------------------------------------------------------------ SOC-SCI 7
    (7, 'SOC-SCI'): {
        'topic': 'Geography: Map skills - latitude, longitude and scale',
        'caps': 'Social Sciences Gr 7, Term 1, Geography: Map skills (focus: Africa) - '
                'latitude and longitude, using an atlas, scale (word, line and number scales) '
                'and calculating distance',
        'summary': 'Learners revise the grid of latitude and longitude, use coordinates and the '
                   'atlas index to find places in Africa, and use map scales to measure distance.',
        'days': [
            {
                'title': 'Latitude and longitude',
                'minutes': 45,
                'objectives': [
                    'I can explain what lines of latitude and longitude are.',
                    'I can name the Equator, the Prime (Greenwich) Meridian and the Tropics.',
                    'I can say whether a place is north or south, east or west.',
                ],
                'notes': (
                    '<p>To find any place on Earth, map makers draw an imaginary grid over the globe. '
                    'The grid is made of two sets of lines.</p>'
                    '<p><strong>Lines of latitude</strong> run from west to east, parallel to each other. '
                    'They measure how far a place is <em>north or south</em> of the <strong>Equator</strong> '
                    '(0°). The Equator divides the Earth into the Northern and Southern Hemispheres. '
                    'Latitude goes up to 90° N (North Pole) and 90° S (South Pole). Important lines are the '
                    'Tropic of Cancer (23½° N), the Tropic of Capricorn (23½° S), the Arctic Circle and the '
                    'Antarctic Circle.</p>'
                    '<p><strong>Lines of longitude</strong> (meridians) run from the North Pole to the South Pole. '
                    'They measure how far a place is <em>east or west</em> of the <strong>Prime Meridian</strong> '
                    '(0°), which passes through Greenwich in London. Longitude goes up to 180° E and 180° W.</p>'
                    '<ul><li>Latitude is always written first, then longitude.</li>'
                    '<li>Always add the direction letter: N or S for latitude, E or W for longitude.</li>'
                    '<li>South Africa lies south of the Equator and east of the Prime Meridian, '
                    'so its coordinates are in degrees S and degrees E.</li></ul>'
                ),
                'key_terms': [
                    ('Latitude', 'Distance in degrees north or south of the Equator'),
                    ('Longitude', 'Distance in degrees east or west of the Prime Meridian'),
                    ('Equator', 'The 0° line of latitude around the middle of the Earth'),
                    ('Prime Meridian', 'The 0° line of longitude through Greenwich, London'),
                    ('Hemisphere', 'Half of the Earth'),
                ],
                'example': {
                    'title': 'Class activity: the human grid',
                    'html': (
                        '<p>Use masking tape to mark an Equator (west to east) and a Prime Meridian '
                        '(north to south) on the classroom floor.</p>'
                        '<ol><li>A learner stands two steps north of the Equator and three steps east of the '
                        'meridian. The class says: "north and east".</li>'
                        '<li>Repeat for other positions. Which hemisphere is each learner in?</li>'
                        '<li>Link it to the globe: Cape Town is about 34° S, 18° E - south and east.</li></ol>'
                    ),
                },
                'video': {'id': 'NldgslCvJrI',
                          'title': 'Longitude and Latitude Explained: Map Skills | Geography | ClickView',
                          'channel': 'ClickView', 'minutes': 4},
                'worksheet': {
                    'instructions': 'Use an atlas or a world map to answer the questions.',
                    'exercises': [
                        '1. What is the latitude of the Equator?',
                        '2. Through which city does the Prime Meridian pass?',
                        '3. In which two hemispheres (N/S and E/W) is South Africa?',
                        '4. Name the line of latitude at 23½° S.',
                        '5. Do lines of longitude meet? If so, where?',
                        '6. Explain the difference between latitude and longitude in your own words.',
                    ],
                },
                'quiz': [
                    ('mcq', 'Which line is 0° latitude?',
                     ['The Prime Meridian', 'The Equator', 'The Tropic of Cancer', 'The Arctic Circle'], 1),
                    ('tf', 'Lines of longitude measure distance east or west of the Prime Meridian.', True),
                    ('mcq', 'South Africa lies in which hemispheres?',
                     ['Northern and Western', 'Northern and Eastern', 'Southern and Eastern',
                      'Southern and Western'], 2),
                    ('tf', 'When writing coordinates, longitude is written before latitude.', False),
                ],
                'homework': {
                    'title': 'Lines on the globe',
                    'instructions': 'Draw a simple globe and label it neatly.',
                    'tasks': [
                        'Draw a circle and label the Equator, the Tropics of Cancer and Capricorn and the Prime Meridian.',
                        'Mark the Northern and Southern Hemispheres.',
                        'Write two sentences explaining why we need latitude and longitude.',
                    ],
                    'marks': 10,
                },
            },
            {
                'title': 'Finding places in Africa with coordinates and the atlas index',
                'minutes': 45,
                'objectives': [
                    'I can read and write the coordinates of a place in degrees.',
                    'I can find a place on a map of Africa from its coordinates.',
                    'I can use the atlas index to find a place.',
                ],
                'notes': (
                    '<p>Coordinates give the <strong>exact position</strong> of a place. We write latitude first, '
                    'then longitude, for example Nairobi is about <strong>1° S; 37° E</strong>.</p>'
                    '<p><strong>Steps to find a place from its coordinates:</strong></p>'
                    '<ol><li>Find the line of latitude on the side of the map (count north or south from the Equator).</li>'
                    '<li>Find the line of longitude at the top or bottom of the map (count east or west from Greenwich).</li>'
                    '<li>Follow both lines until they cross. The place is where they meet.</li></ol>'
                    '<p>Each degree can be divided into 60 <strong>minutes</strong> (written <em>\'</em>), '
                    'so 33° 55\' S is a little less than 34° S. This gives more accurate positions.</p>'
                    '<p>The <strong>atlas index</strong> is an alphabetical list at the back of an atlas. For each '
                    'place it gives the page number, the coordinates and often a grid square (such as C4). '
                    'Use the page number to open the correct map, then use the coordinates or grid square '
                    'to find the place.</p>'
                ),
                'key_terms': [
                    ('Coordinates', 'The latitude and longitude that give a place\'s exact position'),
                    ('Degree (°)', 'The unit used to measure latitude and longitude'),
                    ('Minute (\')', 'One sixtieth of a degree'),
                    ('Atlas index', 'Alphabetical list of places with page numbers and coordinates'),
                ],
                'example': {
                    'title': 'Worked example: reading coordinates',
                    'html': (
                        '<p><strong>Question:</strong> A city lies at 30° N; 31° E. Which city is it?</p>'
                        '<p><strong>Step 1:</strong> 30° N is north of the Equator, in North Africa.</p>'
                        '<p><strong>Step 2:</strong> 31° E is east of the Prime Meridian.</p>'
                        '<p><strong>Step 3:</strong> Where they cross, on the Nile River, is <strong>Cairo</strong> (Egypt).</p>'
                        '<p>Now try: 26° S; 28° E (answer: Johannesburg).</p>'
                    ),
                },
                'video': {'id': 'IgZfnlHYrfI', 'title': 'Mapwork plotting places latitude longitude',
                          'channel': 'Fish', 'minutes': 6},
                'worksheet': {
                    'instructions': 'Use the map of Africa in your atlas. Give coordinates in whole degrees.',
                    'exercises': [
                        '1. Give the approximate coordinates of Cape Town.',
                        '2. Which capital city lies at about 1° S; 37° E?',
                        '3. Which capital city lies at about 6° N; 3° E?',
                        '4. Look up Timbuktu in the atlas index. Write down its page number and coordinates.',
                        '5. Is Lusaka north or south of Harare? Use latitude to explain.',
                        '6. Why is it useful to divide a degree into minutes?',
                    ],
                },
                'quiz': [
                    ('mcq', 'Which is written correctly?',
                     ['28° E; 26° S', '26°; 28°', '26° S; 28° E', 'S 26; E 28 degrees'], 2),
                    ('mcq', 'How many minutes are there in one degree?', ['60', '100', '10', '360'], 0),
                    ('tf', 'An atlas index lists places in alphabetical order.', True),
                    ('tf', 'Cairo lies in the Southern Hemisphere.', False),
                ],
                'homework': {
                    'title': 'Coordinates treasure hunt',
                    'instructions': 'Use an atlas or an online map to complete the tasks.',
                    'tasks': [
                        'Write the approximate coordinates of five African capital cities.',
                        'Swap your list with a family member: can they find the cities from the coordinates?',
                        'Find your own town and write its coordinates.',
                    ],
                    'marks': 10,
                },
            },
            {
                'title': 'Map scale and measuring distance',
                'minutes': 45,
                'objectives': [
                    'I can identify word, line and number (ratio) scales.',
                    'I can use a line scale to measure distance on a map.',
                    'I can tell the difference between large-scale and small-scale maps.',
                ],
                'notes': (
                    '<p>A map is much smaller than the real area it shows. The <strong>scale</strong> tells us how '
                    'much smaller. It compares a distance on the map with the real distance on the ground.</p>'
                    '<ul><li><strong>Word scale:</strong> "1 cm represents 10 km".</li>'
                    '<li><strong>Line (linear) scale:</strong> a ruled line divided into sections, each labelled '
                    'with a real distance. It stays correct even if the map is enlarged or reduced.</li>'
                    '<li><strong>Number (ratio) scale:</strong> 1 : 50 000, which means 1 unit on the map is '
                    '50 000 of the same units on the ground (1 cm = 50 000 cm = 500 m).</li></ul>'
                    '<p><strong>Measuring a straight-line distance:</strong> place the edge of a strip of paper '
                    'between two points, mark both points, then lay the paper on the line scale and read off '
                    'the distance. For a curved road or river, use a piece of string along the route.</p>'
                    '<p>A <strong>large-scale map</strong> (e.g. 1 : 10 000) shows a small area in a lot of detail, '
                    'like a street map. A <strong>small-scale map</strong> (e.g. 1 : 10 000 000) shows a large area, '
                    'such as Africa, with little detail.</p>'
                ),
                'key_terms': [
                    ('Scale', 'The relationship between map distance and real distance'),
                    ('Line scale', 'A divided line used to measure real distances'),
                    ('Ratio scale', 'A scale written as 1 : 50 000'),
                    ('Large-scale map', 'Shows a small area in great detail'),
                ],
                'example': {
                    'title': 'Worked example: using a word scale',
                    'html': (
                        '<p>The scale of a map is <strong>1 cm represents 25 km</strong>. Two towns are 6 cm apart on the map.</p>'
                        '<p>Real distance = 6 x 25 km = <strong>150 km</strong>.</p>'
                        '<p>With a ratio scale of 1 : 50 000: 4 cm on the map = 4 x 50 000 cm = 200 000 cm = 2 000 m '
                        '= <strong>2 km</strong>.</p>'
                    ),
                },
                'video': {'id': 'u_xHCRrlvQU',
                          'title': 'Types of Maps and Map Scale - Learn How to Read and Use Maps',
                          'channel': 'Miacademy & MiaPrep Learning Channel', 'minutes': 6},
                'worksheet': {
                    'instructions': 'Show your working for each calculation.',
                    'exercises': [
                        '1. Name the three types of scale and give an example of each.',
                        '2. Scale: 1 cm represents 5 km. Two villages are 7 cm apart. What is the real distance?',
                        '3. Scale: 1 : 50 000. A road is 3 cm long on the map. How long is it in km?',
                        '4. Which type of scale stays correct when a map is photocopied larger? Why?',
                        '5. Is a street map of your town a large-scale or a small-scale map?',
                        '6. How would you measure the length of a winding river on a map?',
                    ],
                },
                'quiz': [
                    ('mcq', 'On a 1 : 50 000 map, what does 1 cm represent?',
                     ['50 m', '5 km', '500 m', '50 km'], 2),
                    ('tf', 'A small-scale map shows a large area with little detail.', True),
                    ('mcq', 'Scale: 1 cm represents 10 km. Two towns are 4 cm apart. How far apart are they?',
                     ['14 km', '40 km', '4 km', '400 km'], 1),
                    ('tf', '"1 cm represents 2 km" is an example of a line scale.', False),
                ],
                'homework': {
                    'title': 'Scale it up',
                    'instructions': 'Draw a simple map of your home and street.',
                    'tasks': [
                        'Draw a map of your street or neighbourhood with a key.',
                        'Add a line scale and a word scale to your map.',
                        'Use your scale to work out the distance from your home to one other place.',
                    ],
                    'marks': 15,
                },
            },
        ],
    },

    # ------------------------------------------------------------------ SOC-SCI 8
    (8, 'SOC-SCI'): {
        'topic': 'Geography: Maps and globes',
        'caps': 'Social Sciences Gr 8, Term 1, Geography: Maps and globes - the globe and the '
                'Earth\'s movements, latitude and longitude (degrees and minutes), map projections',
        'summary': 'Learners study the globe as a model of the Earth, how the Earth rotates and '
                   'revolves, locate places in degrees and minutes, and compare map projections.',
        'days': [
            {
                'title': 'The globe: a model of the Earth and its movements',
                'minutes': 45,
                'objectives': [
                    'I can explain why a globe is the most accurate model of the Earth.',
                    'Learners will describe the Earth\'s rotation and revolution.',
                    'I can explain why we have leap years.',
                ],
                'notes': (
                    '<p>A <strong>globe</strong> is a round model of the Earth. Because it has the same shape as the '
                    'Earth, it shows the true shape, size and position of continents and oceans. Its drawback '
                    'is that it is bulky and can only show the whole world in very little detail.</p>'
                    '<p>The Earth is tilted on its <strong>axis</strong> at about 23½°. The axis is an imaginary line '
                    'through the North and South Poles.</p>'
                    '<ul><li><strong>Rotation:</strong> the Earth spins on its axis from west to east once every '
                    'about 24 hours. Rotation causes <strong>day and night</strong>. The exact time for one '
                    'turn measured against the stars is a <em>sidereal day</em> (about 23 hours 56 minutes).</li>'
                    '<li><strong>Revolution:</strong> the Earth travels around the Sun in an orbit. One revolution '
                    'takes about 365¼ days. Revolution together with the tilt causes the <strong>seasons</strong>.</li></ul>'
                    '<p>Because a year is about 365¼ days, the extra quarter days add up to one whole day every '
                    'four years. We add it as 29 February in a <strong>leap year</strong> (e.g. 2024, 2028).</p>'
                ),
                'key_terms': [
                    ('Globe', 'A spherical model of the Earth'),
                    ('Axis', 'Imaginary line through the poles around which the Earth spins'),
                    ('Rotation', 'The Earth spinning on its axis (about 24 hours)'),
                    ('Revolution', 'The Earth moving around the Sun (about 365¼ days)'),
                    ('Leap year', 'A year of 366 days, every four years'),
                ],
                'example': {
                    'title': 'Class activity: torch and globe',
                    'html': (
                        '<p>Darken the room. One learner holds a torch (the Sun). Another slowly turns a globe '
                        'from west to east.</p>'
                        '<ol><li>Stick a small paper marker on South Africa. When is it day? When is it night?</li>'
                        '<li>Walk the globe around the torch, keeping the tilt pointing the same way. '
                        'Notice when the Southern Hemisphere leans towards the light (summer).</li>'
                        '<li>Discuss: what would happen if the Earth did not rotate?</li></ol>'
                    ),
                },
                'video': {'id': 'l64YwNl1wr0', 'title': "Earth's Rotation & Revolution: Crash Course Kids 8.1",
                          'channel': 'Crash Course Kids', 'minutes': 4},
                'worksheet': {
                    'instructions': 'Answer in full sentences.',
                    'exercises': [
                        '1. Give one advantage and one disadvantage of a globe compared to a flat map.',
                        '2. What is the Earth\'s axis, and at what angle is it tilted?',
                        '3. Explain how rotation causes day and night.',
                        '4. How long does one revolution of the Earth around the Sun take?',
                        '5. Why do we add 29 February every four years?',
                        '6. Is 2026 a leap year? Name the next leap year.',
                    ],
                },
                'quiz': [
                    ('mcq', 'What causes day and night?',
                     ['The Earth\'s revolution', 'The Earth\'s rotation', 'The Moon\'s orbit', 'The tilt of the axis alone'], 1),
                    ('tf', 'The Earth takes about 365¼ days to revolve around the Sun.', True),
                    ('mcq', 'Which of these years is a leap year?', ['2026', '2027', '2025', '2028'], 3),
                    ('tf', 'A globe distorts the shapes of the continents more than a flat world map does.', False),
                ],
                'homework': {
                    'title': 'Day, night and leap years',
                    'instructions': 'Draw and explain.',
                    'tasks': [
                        'Draw a labelled diagram of the Earth rotating, showing the day side and the night side.',
                        'Explain in three or four sentences why leap years are needed.',
                    ],
                    'marks': 10,
                },
            },
            {
                'title': 'Latitude and longitude in degrees and minutes',
                'minutes': 45,
                'objectives': [
                    'I can read and write coordinates in degrees and minutes.',
                    'I can locate places in South Africa accurately on an atlas map.',
                    'I can use the atlas index to find a place.',
                ],
                'notes': (
                    '<p>In Grade 7 you used whole degrees. To be more accurate, each degree is divided into '
                    '<strong>60 minutes</strong>. For example, Cape Town is at about <strong>33° 55\' S; 18° 25\' E</strong>.</p>'
                    '<p><strong>How to work out minutes on an atlas map:</strong></p>'
                    '<ol><li>Find the two printed lines of latitude on either side of the place (e.g. 33° S and 34° S).</li>'
                    '<li>Measure the distance between the two lines in millimetres (say 30 mm). This gap = 60\'.</li>'
                    '<li>Measure from the lower-numbered line to the place (say 15 mm).</li>'
                    '<li>Minutes = (15 / 30) x 60 = 30\'. So the latitude is 33° 30\' S.</li>'
                    '<li>Repeat the same steps for longitude.</li></ol>'
                    '<p>Remember: south of the Equator, latitude numbers <em>increase towards the bottom</em> '
                    'of the map. East of Greenwich, longitude numbers increase to the right.</p>'
                    '<p>The <strong>atlas index</strong> gives the page and coordinates for every place, so you '
                    'can check your answers.</p>'
                ),
                'key_terms': [
                    ('Minute (\')', 'One sixtieth (1/60) of a degree'),
                    ('Coordinates', 'Latitude and longitude written together, latitude first'),
                    ('Atlas index', 'Alphabetical list of places with page number and coordinates'),
                ],
                'example': {
                    'title': 'Worked example: calculating minutes',
                    'html': (
                        '<p>On a map, the lines for 29° S and 30° S are 40 mm apart. A town lies 10 mm below '
                        'the 29° S line.</p>'
                        '<p>Minutes = (10 / 40) x 60 = 15\'.</p>'
                        '<p>Latitude = <strong>29° 15\' S</strong>.</p>'
                        '<p>The same town lies 20 mm east of 31° E, and the lines for 31° E and 32° E are 40 mm '
                        'apart: (20 / 40) x 60 = 30\', so longitude = <strong>31° 30\' E</strong>.</p>'
                    ),
                },
                'video': {'id': 'FyJPQG99Hbk', 'title': 'Mapwork coordinates degrees, minutes and seconds',
                          'channel': 'Fish', 'minutes': 8},
                'worksheet': {
                    'instructions': 'Use your atlas map of South Africa. Show your calculations.',
                    'exercises': [
                        '1. How many minutes are in one degree? How many minutes in half a degree?',
                        '2. Lines 25° S and 26° S are 30 mm apart. A place is 20 mm below 25° S. Calculate its latitude.',
                        '3. Lines 28° E and 29° E are 36 mm apart. A place is 9 mm east of 28° E. Calculate its longitude.',
                        '4. Give the coordinates of Pretoria in degrees and minutes (use the atlas index to check).',
                        '5. Which city is at about 29° 51\' S; 31° 01\' E?',
                        '6. Why are degrees and minutes more useful than whole degrees?',
                    ],
                },
                'quiz': [
                    ('mcq', 'How many minutes are in 1 degree?', ['100', '30', '24', '60'], 3),
                    ('mcq', 'Lines 33° S and 34° S are 30 mm apart; a place is 10 mm below 33° S. Its latitude is:',
                     ['33° 10\' S', '33° 20\' S', '33° 30\' S', '34° 10\' S'], 1),
                    ('tf', 'In coordinates, latitude is written before longitude.', True),
                    ('tf', '30\' is the same as one quarter of a degree.', False),
                ],
                'homework': {
                    'title': 'Pinpoint South Africa',
                    'instructions': 'Use an atlas or a map app.',
                    'tasks': [
                        'Find the coordinates, in degrees and minutes, of the capital city of each of three provinces.',
                        'Find the coordinates of your own town.',
                        'Explain to someone at home how coordinates work; write down one question they asked.',
                    ],
                    'marks': 10,
                },
            },
            {
                'title': 'Map projections and satellite images',
                'minutes': 45,
                'objectives': [
                    'I can explain why all flat world maps are distorted.',
                    'I can compare the Mercator and Peters (Gall-Peters) projections.',
                    'Learners will describe how satellite images are used to make maps.',
                ],
                'notes': (
                    '<p>It is impossible to flatten a round surface without stretching or tearing it. A '
                    '<strong>map projection</strong> is a method of showing the curved surface of the Earth on a '
                    'flat map. Every projection distorts something: shape, area, distance or direction.</p>'
                    '<ul><li><strong>Mercator projection</strong> (1569): keeps shapes and directions correct, '
                    'so it was ideal for sailors. But areas near the poles look far too big. Greenland looks '
                    'as big as Africa, yet Africa is about 14 times larger.</li>'
                    '<li><strong>Peters (Gall-Peters) projection</strong>: shows the correct <em>area</em> of '
                    'countries, so Africa and South America appear their true size, but shapes are '
                    'stretched.</li>'
                    '<li>Other projections (e.g. Robinson) try to balance the distortions.</li></ul>'
                    '<p>The projection we choose affects how we see the world: maps that enlarge Europe and '
                    'North America can make Africa seem less important than it is.</p>'
                    '<p><strong>Satellite images</strong> are photographs of the Earth taken from space. They help '
                    'map makers update maps and show land use, weather, floods and fires.</p>'
                ),
                'key_terms': [
                    ('Map projection', 'A way of showing the curved Earth on a flat surface'),
                    ('Distortion', 'Change in true shape, area, distance or direction'),
                    ('Mercator projection', 'Keeps shape and direction; enlarges areas near the poles'),
                    ('Peters projection', 'Keeps true area; stretches shapes'),
                    ('Satellite image', 'Picture of the Earth taken from a satellite in space'),
                ],
                'example': {
                    'title': 'Class activity: the orange peel map',
                    'html': (
                        '<ol><li>Draw continents roughly on an orange with a marker.</li>'
                        '<li>Peel the orange carefully and try to flatten the peel.</li>'
                        '<li>Discuss: what happened to the shapes? Where did the peel tear or stretch?</li>'
                        '<li>Compare a Mercator world map and a Peters world map. Find Greenland and Africa '
                        'on both and compare their sizes.</li></ol>'
                    ),
                },
                'video': {'id': '8_cAY_rQpzM', 'title': 'Map Projections – Why Do We Have Different Maps of the Earth?',
                          'channel': 'Kurzgesagt – In a Nutshell', 'minutes': 6},
                'worksheet': {
                    'instructions': 'Use the notes and your atlas.',
                    'exercises': [
                        '1. What is a map projection?',
                        '2. Why does every flat world map have some distortion?',
                        '3. Give one strength and one weakness of the Mercator projection.',
                        '4. What does the Peters projection show correctly?',
                        '5. Greenland and Africa look similar in size on a Mercator map. Which is really larger?',
                        '6. Name two ways satellite images are useful.',
                    ],
                },
                'quiz': [
                    ('mcq', 'Which projection shows the true area of countries?',
                     ['Mercator', 'Peters (Gall-Peters)', 'A street map', 'None of them'], 1),
                    ('tf', 'On a Mercator map, areas near the poles appear larger than they really are.', True),
                    ('mcq', 'Why was the Mercator projection popular with sailors?',
                     ['It shows true area', 'It keeps directions correct', 'It shows mountains', 'It is round'], 1),
                    ('tf', 'It is possible to make a flat map of the whole world with no distortion at all.', False),
                ],
                'homework': {
                    'title': 'Which map is fair?',
                    'instructions': 'Look at two world maps (atlas or internet).',
                    'tasks': [
                        'Compare the size of Africa on a Mercator map and on a Peters map. Describe the difference.',
                        'Write a paragraph: which projection would you hang in a classroom, and why?',
                    ],
                    'marks': 10,
                },
            },
        ],
    },

    # ------------------------------------------------------------------ SOC-SCI 9
    (9, 'SOC-SCI'): {
        'topic': 'Geography: Map skills - contours, orthophoto maps and topographic maps',
        'caps': 'Social Sciences Gr 9, Term 1, Geography: Map skills - contour lines and '
                'landforms, 1:10 000 orthophoto maps, 1:50 000 topographic maps',
        'summary': 'Learners interpret contour lines and slopes, read vertical aerial photographs '
                   'and orthophoto maps, and identify features on 1:50 000 topographic maps.',
        'days': [
            {
                'title': 'Contour lines, slopes and landforms',
                'minutes': 50,
                'objectives': [
                    'I can explain what contour lines and the contour interval are.',
                    'I can identify steep, gentle, concave and convex slopes from contour spacing.',
                    'I can recognise hills, valleys and spurs from contour patterns.',
                ],
                'notes': (
                    '<p>A <strong>contour line</strong> joins points on a map that are the same height above sea level. '
                    'The difference in height between two neighbouring contour lines is the '
                    '<strong>contour interval</strong> (20 m on South African 1:50 000 maps).</p>'
                    '<p><strong>Rules for reading contours:</strong></p>'
                    '<ul><li>Lines <strong>close together</strong> = a <strong>steep</strong> slope.</li>'
                    '<li>Lines <strong>far apart</strong> = a <strong>gentle</strong> slope.</li>'
                    '<li>Evenly spaced lines = a uniform slope.</li>'
                    '<li><strong>Concave</strong> slope: lines close together at the top, far apart at the bottom.</li>'
                    '<li><strong>Convex</strong> slope: lines far apart at the top, close together at the bottom.</li>'
                    '<li>Contour lines never cross.</li></ul>'
                    '<p><strong>Landforms:</strong> a <em>hill</em> shows as closed rings with the highest value in the '
                    'middle. A <em>river valley</em> shows as V-shapes pointing <strong>upstream</strong> (towards higher '
                    'ground), with a river at the bottom. A <em>spur</em> is a ridge of high ground; its V-shapes point '
                    '<strong>downhill</strong> (towards lower ground). Other height clues include trigonometrical '
                    'stations (a triangle with a height) and spot heights (a dot with a height).</p>'
                ),
                'key_terms': [
                    ('Contour line', 'A line joining places of equal height above sea level'),
                    ('Contour interval', 'The height difference between neighbouring contours'),
                    ('Spur', 'A ridge of high ground sticking out from higher land'),
                    ('Trigonometrical station', 'A surveyed point of exact height, shown by a triangle'),
                    ('Spot height', 'A dot showing the height at a point'),
                ],
                'example': {
                    'title': 'Class activity: the fist mountain',
                    'html': (
                        '<ol><li>Make a fist. Your knuckles are a mountain range.</li>'
                        '<li>With a washable marker, draw a line around your fist at the same "height" '
                        '(about 1 cm from the table), then at 2 cm and 3 cm.</li>'
                        '<li>Open your hand flat: you now see contour lines. Where are they close together? '
                        'That is where your fist was steepest.</li>'
                        '<li>Find a valley between two knuckles: notice the V-shape.</li></ol>'
                    ),
                },
                'video': {'id': 'JLjzP4FrYDQ', 'title': 'Contour Lines, Slopes, River Valleys & Spurs',
                          'channel': 'Magfar Online School', 'minutes': 8},
                'worksheet': {
                    'instructions': 'Answer the questions. Draw sketches where asked.',
                    'exercises': [
                        '1. Define a contour line and a contour interval.',
                        '2. What is the contour interval on a South African 1:50 000 topographic map?',
                        '3. Sketch contour patterns for a steep slope and for a gentle slope.',
                        '4. How do you tell a concave slope from a convex slope?',
                        '5. Explain how to tell a river valley from a spur.',
                        '6. Why can contour lines never cross?',
                        '7. Name two other ways height is shown on a topographic map.',
                    ],
                },
                'quiz': [
                    ('mcq', 'Contour lines that are very close together show:',
                     ['a gentle slope', 'flat land', 'a steep slope', 'a river'], 2),
                    ('tf', 'In a river valley, the V-shapes of the contours point upstream (towards higher ground).', True),
                    ('mcq', 'A concave slope has contours that are:',
                     ['close at the top and far apart at the bottom', 'far apart at the top and close at the bottom',
                      'evenly spaced', 'crossing each other'], 0),
                    ('tf', 'Contour lines may cross where there is a cliff.', False),
                ],
                'homework': {
                    'title': 'Draw your own landscape',
                    'instructions': 'Use a 20 m contour interval.',
                    'tasks': [
                        'Draw contour lines for a hill 120 m high with a steep side and a gentle side.',
                        'Add a river valley flowing off the hill, with the V-shapes pointing the correct way.',
                        'Label the steep slope, the gentle slope, the valley and a spot height.',
                    ],
                    'marks': 15,
                },
            },
            {
                'title': 'Aerial photographs and 1:10 000 orthophoto maps',
                'minutes': 50,
                'objectives': [
                    'I can explain the difference between an oblique and a vertical aerial photograph.',
                    'I can describe what an orthophoto map is and identify features on one.',
                    'I can use contours on an orthophoto map to describe the landscape.',
                ],
                'notes': (
                    '<p>An <strong>aerial photograph</strong> is taken from an aircraft or drone. An '
                    '<em>oblique</em> photograph is taken at an angle and shows the sides of buildings. A '
                    '<strong>vertical</strong> aerial photograph is taken straight down, so we only see the tops '
                    'of objects (roofs, tree crowns).</p>'
                    '<p>An <strong>orthophoto map</strong> is a corrected vertical aerial photograph with map '
                    'information printed on it: <strong>contour lines</strong> (usually a 5 m interval), names, '
                    'spot heights and a grid. In South Africa orthophoto maps have a scale of <strong>1:10 000</strong>, '
                    'so 1 cm on the map = 100 m on the ground. They are large-scale and show a lot of detail.</p>'
                    '<p><strong>Identifying features:</strong></p>'
                    '<ul><li><em>Tone</em> (light or dark): water and dense vegetation look dark; dry ground and '
                    'concrete look light.</li>'
                    '<li><em>Shape and pattern</em>: fields form regular blocks, rivers wind, roads are long lines.</li>'
                    '<li><em>Size and shadow</em> help tell houses from factories or trees from bushes.</li></ul>'
                    '<p>Orthophoto maps are used by town planners, farmers and engineers because they show what '
                    'the land really looks like, together with height information.</p>'
                ),
                'key_terms': [
                    ('Vertical aerial photograph', 'A photo taken looking straight down from the air'),
                    ('Oblique aerial photograph', 'A photo taken from the air at an angle'),
                    ('Orthophoto map', 'A corrected vertical aerial photo with contours and names, scale 1:10 000'),
                    ('Tone', 'How light or dark a feature appears on a photo'),
                ],
                'example': {
                    'title': 'Worked example: orthophoto scale',
                    'html': (
                        '<p>On a 1:10 000 orthophoto map, a dam wall measures 3,5 cm.</p>'
                        '<p>Real length = 3,5 x 10 000 cm = 35 000 cm = <strong>350 m</strong>.</p>'
                        '<p>Shortcut: on 1:10 000, 1 cm = 100 m, so 3,5 cm = 350 m.</p>'
                        '<p>Then describe: the dam appears <em>dark</em> (water) with a light straight edge (the wall).</p>'
                    ),
                },
                'video': {'id': 'aPbD2TwH7qM', 'title': 'Understanding Orthophoto Maps - Grade 9 Term 1 Geography',
                          'channel': 'Magfar Online School', 'minutes': 8},
                'worksheet': {
                    'instructions': 'Use the notes (and an orthophoto map extract if available).',
                    'exercises': [
                        '1. What is the difference between a vertical and an oblique aerial photograph?',
                        '2. What is the scale of a South African orthophoto map? What does 1 cm represent?',
                        '3. A road is 6 cm long on a 1:10 000 map. Calculate its real length in metres.',
                        '4. Why would a river or dam appear dark on an orthophoto?',
                        '5. Name three clues (tone, shape, pattern, size, shadow) you would use to identify a sports field.',
                        '6. Give two uses of orthophoto maps.',
                    ],
                },
                'quiz': [
                    ('mcq', 'A vertical aerial photograph is taken:',
                     ['at an angle', 'from the ground', 'straight down', 'from a satellite only'], 2),
                    ('mcq', 'On a 1:10 000 orthophoto map, 1 cm represents:',
                     ['10 m', '100 m', '1 km', '10 km'], 1),
                    ('tf', 'Orthophoto maps show contour lines printed over a photograph.', True),
                    ('tf', 'An orthophoto map is a small-scale map.', False),
                ],
                'homework': {
                    'title': 'A bird\'s-eye view',
                    'instructions': 'Use a free online satellite map view of your area, or a printed photo.',
                    'tasks': [
                        'Sketch a vertical view of your school or street showing at least five features.',
                        'Add a key and describe how tone and shape helped you identify each feature.',
                    ],
                    'marks': 10,
                },
            },
            {
                'title': 'Reading 1:50 000 topographic maps',
                'minutes': 50,
                'objectives': [
                    'I can use the key to identify natural and constructed features.',
                    'I can calculate real distance using the scale of a 1:50 000 map.',
                    'I can compare a topographic map with an orthophoto map.',
                ],
                'notes': (
                    '<p>A <strong>topographic map</strong> shows the natural features (relief, rivers, vegetation) and '
                    'constructed (human-made) features (roads, railways, buildings, dams) of an area using '
                    '<strong>symbols</strong>, colours and contour lines. In South Africa the standard scale is '
                    '<strong>1:50 000</strong>: 1 cm on the map = 50 000 cm = 500 m on the ground. '
                    'Each map sheet has a reference such as <em>3318CD</em>.</p>'
                    '<p><strong>Reading the key:</strong></p>'
                    '<ul><li>Blue: water features (perennial river = solid line; non-perennial river = broken line).</li>'
                    '<li>Red/black: roads, railways and buildings.</li>'
                    '<li>Green: cultivated land, orchards and vegetation.</li>'
                    '<li>Brown: contour lines (20 m interval).</li></ul>'
                    '<p><strong>Calculating distance:</strong> measure in cm and multiply by 0,5 to get km. '
                    'E.g. 7 cm x 0,5 = 3,5 km.</p>'
                    '<p><strong>Comparing maps:</strong> the topographic map (1:50 000) covers a much bigger '
                    'area than the orthophoto (1:10 000) but with less detail. A feature on the orthophoto '
                    'looks five times larger than on the topographic map.</p>'
                ),
                'key_terms': [
                    ('Topographic map', 'A map using symbols to show natural and human-made features'),
                    ('Perennial river', 'A river that flows all year'),
                    ('Non-perennial river', 'A river that flows only part of the year'),
                    ('Map reference', 'The code that identifies a map sheet, e.g. 3318CD'),
                ],
                'example': {
                    'title': 'Worked example: distance on a 1:50 000 map',
                    'html': (
                        '<p>Two farms are 5,4 cm apart on a 1:50 000 map.</p>'
                        '<p>5,4 cm x 50 000 = 270 000 cm</p>'
                        '<p>270 000 cm / 100 = 2 700 m / 1 000 = <strong>2,7 km</strong></p>'
                        '<p>Shortcut: 5,4 x 0,5 = 2,7 km.</p>'
                    ),
                },
                'video': {'id': 'kJ9TWo0CQd4', 'title': 'How To Read Maps (Map Work Basics)',
                          'channel': 'Closeup Education', 'minutes': 8},
                'worksheet': {
                    'instructions': 'Use the notes and a 1:50 000 map extract with its key if available.',
                    'exercises': [
                        '1. What does 1 cm represent on a 1:50 000 map?',
                        '2. Two schools are 8 cm apart. Calculate the real distance in km.',
                        '3. How is a perennial river shown differently from a non-perennial river?',
                        '4. Name two natural and two constructed features shown on topographic maps.',
                        '5. What colour are contour lines and what is their interval on a 1:50 000 map?',
                        '6. Give one advantage of a topographic map and one of an orthophoto map.',
                    ],
                },
                'quiz': [
                    ('mcq', 'On a 1:50 000 map, 4 cm represents:', ['4 km', '200 m', '2 km', '20 km'], 2),
                    ('tf', 'A non-perennial river is shown with a broken blue line.', True),
                    ('mcq', 'Compared to a 1:10 000 orthophoto, a 1:50 000 topographic map shows:',
                     ['a smaller area in more detail', 'a larger area in less detail',
                      'the same area', 'only rivers'], 1),
                    ('tf', 'Contour lines on a 1:50 000 map are drawn every 5 m.', False),
                ],
                'homework': {
                    'title': 'Design a map key',
                    'instructions': 'Make a mini topographic map of an imaginary place.',
                    'tasks': [
                        'Draw a map of an imaginary area at a scale of 1:50 000, showing a river, roads, a railway and a town.',
                        'Include a key with at least eight symbols, a north arrow and a scale.',
                        'Measure the distance between two features and calculate the real distance.',
                    ],
                    'marks': 20,
                },
            },
        ],
    },

    # ------------------------------------------------------------------ TECH 7
    (7, 'TECH'): {
        'topic': 'Structures: the design process, types of structures and forces',
        'caps': 'Technology Gr 7, Term 1: Structures - the design process (IDMEC), natural and '
                'human-made structures, shell, frame and solid structures, forces and loads',
        'summary': 'Learners meet Technology as a subject through the design process, classify '
                   'structures as shell, frame or solid, and learn how loads and forces act on them.',
        'days': [
            {
                'title': 'What is Technology? The design process',
                'minutes': 45,
                'objectives': [
                    'I can explain what Technology is.',
                    'I can name and describe the five steps of the design process.',
                    'I can identify a problem, need or opportunity in a short scenario.',
                ],
                'notes': (
                    '<p><strong>Technology</strong> is the use of knowledge, skills and resources to solve problems '
                    'and meet people\'s needs and wants. A bridge, a chair, a cellphone and a water tank are all '
                    'technology.</p>'
                    '<p>Technologists solve problems using the <strong>design process</strong>. In CAPS it has five steps '
                    '(remember <strong>IDMEC</strong>):</p>'
                    '<ol><li><strong>Investigate</strong> - find out about the problem; research existing solutions.</li>'
                    '<li><strong>Design</strong> - write a <em>design brief</em> (what you will make), list '
                    '<em>specifications</em> and <em>constraints</em>, and sketch possible ideas.</li>'
                    '<li><strong>Make</strong> - plan the steps, choose tools and materials and build the product safely.</li>'
                    '<li><strong>Evaluate</strong> - test the product: does it meet the specifications?</li>'
                    '<li><strong>Communicate</strong> - share your solution using drawings, notes and presentations.</li></ol>'
                    '<p>The process is not always a straight line. After evaluating, designers often go back and improve '
                    'the design.</p>'
                    '<p><strong>Specifications</strong> are what the product must do or have (e.g. "must hold 1 kg"). '
                    '<strong>Constraints</strong> are limits (e.g. time, cost, materials available).</p>'
                ),
                'key_terms': [
                    ('Technology', 'Using knowledge, skills and resources to solve problems'),
                    ('Design brief', 'A short statement of what will be designed and made'),
                    ('Specifications', 'Requirements the product must meet'),
                    ('Constraints', 'Limits such as time, cost and materials'),
                ],
                'example': {
                    'title': 'Guided activity: write a design brief',
                    'html': (
                        '<p><strong>Scenario:</strong> Learners at a rural school have to cross a small stream to reach '
                        'their classrooms. When it rains, the stepping stones are covered by water.</p>'
                        '<p><strong>Problem:</strong> learners cannot safely cross the stream in wet weather.</p>'
                        '<p><strong>Design brief:</strong> "I will design and make a model of a footbridge that lets '
                        'learners cross the stream safely."</p>'
                        '<p><strong>Specifications:</strong> span 30 cm; hold a 500 g load; have side rails.</p>'
                        '<p><strong>Constraints:</strong> use only paper, straws and glue; finish in two lessons.</p>'
                    ),
                },
                'video': {'id': 'X6aC4l05h1o', 'title': 'Grade 7 | Technology | The Design Process | Week 1 | Lesson 1',
                          'channel': 'Leruo Learning', 'minutes': 10},
                'worksheet': {
                    'instructions': 'Answer the questions in your Technology book.',
                    'exercises': [
                        '1. Write your own definition of Technology.',
                        '2. Name the five steps of the design process in the correct order.',
                        '3. What is the difference between a specification and a constraint?',
                        '4. Give two examples of technology you used today and the need each one meets.',
                        '5. Scenario: books in the class library keep falling over. Write a design brief.',
                        '6. List two specifications and one constraint for your solution in question 5.',
                    ],
                },
                'quiz': [
                    ('mcq', 'Which is the FIRST step of the design process?',
                     ['Make', 'Investigate', 'Evaluate', 'Communicate'], 1),
                    ('tf', 'A constraint is a limit, such as the money or time available.', True),
                    ('mcq', 'Testing your product to see whether it meets the specifications is called:',
                     ['Designing', 'Investigating', 'Evaluating', 'Communicating'], 2),
                    ('tf', 'Once a product is made, designers never go back to improve it.', False),
                ],
                'homework': {
                    'title': 'Technology at home',
                    'instructions': 'Look around your home for examples of technology.',
                    'tasks': [
                        'List five items of technology at home and the problem or need each one solves.',
                        'Choose one item and suggest one improvement a designer could make.',
                    ],
                    'marks': 10,
                },
            },
            {
                'title': 'Types of structures: shell, frame and solid',
                'minutes': 45,
                'objectives': [
                    'I can define a structure and explain its purposes.',
                    'I can tell natural structures from human-made structures.',
                    'I can classify structures as shell, frame or solid.',
                ],
                'notes': (
                    '<p>A <strong>structure</strong> is anything that has a definite shape and can support a load '
                    'without collapsing. Structures <em>support</em> (a table), <em>contain</em> (a bottle), '
                    '<em>protect</em> (a helmet), <em>span</em> (a bridge) or <em>raise</em> things up (a pylon).</p>'
                    '<p><strong>Natural structures</strong> are made by nature (a bird\'s nest, a tortoise shell, '
                    'a tree, our skeleton). <strong>Human-made structures</strong> are designed by people (a house, '
                    'a bridge, a cooldrink can).</p>'
                    '<p>There are three main types:</p>'
                    '<ul><li><strong>Shell structures</strong> are hollow and use a thin outer layer for strength. '
                    'They are light and contain or protect things: an egg, a cooldrink can, a car body, a helmet.</li>'
                    '<li><strong>Frame structures</strong> are made of parts (members) joined together to form a '
                    'skeleton: an electricity pylon, a bicycle frame, the roof trusses of a house, a spider web.</li>'
                    '<li><strong>Solid structures</strong> are made of solid material and get their strength from their '
                    'mass and weight: a dam wall, a brick wall, a pyramid, a mountain.</li></ul>'
                    '<p>Many structures combine types - a house has a solid foundation, a frame roof and walls '
                    'that act like a shell.</p>'
                ),
                'key_terms': [
                    ('Structure', 'Something with a shape that supports a load without collapsing'),
                    ('Shell structure', 'A hollow structure with a thin, strong outer layer'),
                    ('Frame structure', 'A structure of members joined to form a skeleton'),
                    ('Solid structure', 'A structure made of solid material that relies on its mass'),
                ],
                'example': {
                    'title': 'Class activity: sort the structures',
                    'html': (
                        '<p>Display pictures (or real items): an egg, a pylon, a dam wall, a crate, a tent, a '
                        'brick, a bicycle, a helmet, a beehive, a mountain.</p>'
                        '<ol><li>In groups, sort them into shell, frame and solid.</li>'
                        '<li>Then sort them again into natural and human-made.</li>'
                        '<li>Discuss items that fit two groups (a tent is a frame covered with a shell).</li></ol>'
                    ),
                },
                'video': {'id': 'pbBR6u2bR5g',
                          'title': 'Technology grade 7: Structures, classification, Man-made/Natural [Solid, Frame & Shell structures]',
                          'channel': 'Future Hub Academy', 'minutes': 10},
                'worksheet': {
                    'instructions': 'Classify and explain.',
                    'exercises': [
                        '1. Define a structure.',
                        '2. Name four purposes of structures, with an example of each.',
                        '3. Classify as shell, frame or solid: egg, pylon, dam wall, cooldrink can, roof truss, pyramid.',
                        '4. Give two natural and two human-made frame structures.',
                        '5. Why is a shell structure useful for packaging?',
                        '6. Explain why a house can be called a combination structure.',
                    ],
                },
                'quiz': [
                    ('mcq', 'An electricity pylon is an example of a:',
                     ['shell structure', 'solid structure', 'frame structure', 'natural structure'], 2),
                    ('mcq', 'Which of these is a solid structure?',
                     ['A dam wall', 'A bicycle', 'An egg', 'A tent'], 0),
                    ('tf', 'A bird\'s nest is a natural structure.', True),
                    ('tf', 'Shell structures are usually heavy and made of solid material.', False),
                ],
                'homework': {
                    'title': 'Structure hunt',
                    'instructions': 'Find structures at home or in your neighbourhood.',
                    'tasks': [
                        'Find and sketch two shell, two frame and two solid structures.',
                        'Label each one as natural or human-made and write its purpose.',
                    ],
                    'marks': 12,
                },
            },
            {
                'title': 'Loads and forces on structures',
                'minutes': 45,
                'objectives': [
                    'I can explain the difference between static and dynamic loads.',
                    'I can describe tension and compression forces.',
                    'I can test how shape affects the strength of a paper structure.',
                ],
                'notes': (
                    '<p>Every structure must carry a <strong>load</strong> - the weight or force it supports.</p>'
                    '<ul><li>A <strong>static load</strong> does not move or change: the weight of the structure itself, '
                    'or a fridge standing on the floor.</li>'
                    '<li>A <strong>dynamic load</strong> moves or changes: cars driving over a bridge, wind blowing '
                    'against a building, people jumping on a trampoline.</li></ul>'
                    '<p>Loads cause <strong>forces</strong> inside the parts (members) of a structure:</p>'
                    '<ul><li><strong>Compression</strong> squashes or pushes a member together. The legs of a table '
                    'and the pillars of a bridge are in compression.</li>'
                    '<li><strong>Tension</strong> pulls or stretches a member. The cables of a suspension bridge '
                    'and the rope of a swing are in tension.</li></ul>'
                    '<p>A good structure is <strong>strong</strong> (does not break), <strong>stable</strong> '
                    '(does not fall over) and <strong>rigid</strong> (keeps its shape). Engineers make structures '
                    'stronger by choosing suitable materials and shapes, for example folding, rolling or '
                    'corrugating thin sheets, and using triangles in frames.</p>'
                ),
                'key_terms': [
                    ('Load', 'The weight or force a structure must carry'),
                    ('Static load', 'A load that does not move'),
                    ('Dynamic load', 'A load that moves or changes'),
                    ('Compression', 'A force that squashes a member'),
                    ('Tension', 'A force that stretches a member'),
                ],
                'example': {
                    'title': 'Class investigation: paper columns',
                    'html': (
                        '<ol><li>Each group gets three A4 sheets.</li>'
                        '<li>Fold one into a triangular column, roll one into a round tube, fold one into a square column. '
                        'Tape each closed.</li>'
                        '<li>Stand each upright and carefully stack textbooks on top until it buckles.</li>'
                        '<li>Record the number of books for each. Which shape was strongest under compression? '
                        '(Usually the round tube.)</li></ol>'
                    ),
                },
                'video': {'id': 'C20gplgvBUY', 'title': 'What is tension and Compression? Differences - Forces in Buildings & Bridges',
                          'channel': 'Iamcivilengineer', 'minutes': 5},
                'worksheet': {
                    'instructions': 'Answer the questions and draw where asked.',
                    'exercises': [
                        '1. What is a load?',
                        '2. Classify as static or dynamic: a roof, wind, a bus crossing a bridge, a bookshelf full of books.',
                        '3. Explain the difference between tension and compression.',
                        '4. Is the rope of a swing in tension or compression? Explain.',
                        '5. Draw a table with a heavy box on it. Use arrows to show the compression in the legs.',
                        '6. Name three qualities a good structure must have.',
                    ],
                },
                'quiz': [
                    ('mcq', 'Wind blowing against a building is a:',
                     ['static load', 'dynamic load', 'tension member', 'shell structure'], 1),
                    ('tf', 'The legs of a table are in compression.', True),
                    ('mcq', 'Which force stretches or pulls a member?', ['Compression', 'Gravity', 'Tension', 'Friction'], 2),
                    ('tf', 'A rigid structure changes shape easily when a load is applied.', False),
                ],
                'homework': {
                    'title': 'Forces in action',
                    'instructions': 'Look for structures carrying loads.',
                    'tasks': [
                        'Sketch one structure at home that carries a static load and one that carries a dynamic load.',
                        'On each sketch, mark one member in tension or compression with arrows.',
                    ],
                    'marks': 10,
                },
            },
        ],
    },

    # ------------------------------------------------------------------ TECH 8
    (8, 'TECH'): {
        'topic': 'Structures: frame structures, forces and strengthening',
        'caps': 'Technology Gr 8, Term 1: Structures - frame structures, forces in structural '
                'members (tension, compression, bending, shear, torsion), triangulation and '
                'strengthening structures',
        'summary': 'Learners analyse frame structures, identify the forces acting in their members, '
                   'and use triangulation and gussets to make frames rigid.',
        'days': [
            {
                'title': 'Frame structures and their members',
                'minutes': 45,
                'objectives': [
                    'I can describe a frame structure and give examples.',
                    'I can name the members of a frame (struts, ties, beams, columns).',
                    'I can explain the advantages of frame structures.',
                ],
                'notes': (
                    '<p>A <strong>frame structure</strong> is made of separate parts called <strong>members</strong> '
                    'joined together to form a framework that carries loads. Examples: a roof truss, an '
                    'electricity pylon, a crane, a bicycle frame, scaffolding and the steel skeleton of a skyscraper.</p>'
                    '<p><strong>Members of a frame:</strong></p>'
                    '<ul><li><strong>Struts</strong> are members in <em>compression</em> (being pushed).</li>'
                    '<li><strong>Ties</strong> are members in <em>tension</em> (being pulled). A tie can be a thin rod or '
                    'cable because it is only pulled.</li>'
                    '<li><strong>Beams</strong> are horizontal members that carry loads across a gap and bend.</li>'
                    '<li><strong>Columns</strong> are vertical members that carry loads down to the foundation.</li></ul>'
                    '<p><strong>Why use frames?</strong> They use less material than solid structures, so they are '
                    '<em>lighter and cheaper</em>, they can be very tall or span long distances, and wind can blow '
                    'through them. Their weakness is the <strong>joints</strong>: a square frame can easily be pushed '
                    'into a parallelogram unless it is braced.</p>'
                    '<p>Frames are often covered (cladding, a roof, a tent cover) to make shelters.</p>'
                ),
                'key_terms': [
                    ('Member', 'One part (bar or rod) of a frame structure'),
                    ('Strut', 'A member in compression'),
                    ('Tie', 'A member in tension'),
                    ('Beam', 'A horizontal member that spans a gap'),
                    ('Column', 'A vertical member carrying loads down'),
                ],
                'example': {
                    'title': 'Class activity: straw frames',
                    'html': (
                        '<ol><li>Join four straws with pipe-cleaner or paper-clip joints to make a square.</li>'
                        '<li>Push gently on one corner. What happens? (It collapses into a parallelogram.)</li>'
                        '<li>Make a triangle from three straws and push on a corner. What happens? (It keeps its shape.)</li>'
                        '<li>Discuss: what does this tell us about building pylons and roof trusses?</li></ol>'
                    ),
                },
                'video': {'id': 'q_HUizMuEAc', 'title': 'Frame Structures Explained | Grade 8 Technology Term 1',
                          'channel': 'Magfar Online School', 'minutes': 8},
                'worksheet': {
                    'instructions': 'Answer in full sentences.',
                    'exercises': [
                        '1. Define a frame structure and give four examples.',
                        '2. What is the difference between a strut and a tie?',
                        '3. Why can a tie be made from a thin cable but a strut cannot?',
                        '4. Give three advantages of frame structures over solid structures.',
                        '5. What is the weakest part of a frame structure?',
                        '6. Sketch a simple roof truss and label one beam and one column or strut.',
                    ],
                },
                'quiz': [
                    ('mcq', 'A member in compression is called a:', ['tie', 'cable', 'strut', 'gusset'], 2),
                    ('tf', 'Frame structures usually use less material than solid structures.', True),
                    ('mcq', 'Which is a frame structure?',
                     ['A dam wall', 'A crane', 'An egg', 'A brick'], 1),
                    ('tf', 'A square frame with no bracing is very rigid.', False),
                ],
                'homework': {
                    'title': 'Frames around us',
                    'instructions': 'Look for frame structures in your neighbourhood.',
                    'tasks': [
                        'Sketch one frame structure you can see (a gate, pylon, roof, swing or bicycle).',
                        'Label at least three members and say whether each is a strut, tie, beam or column.',
                    ],
                    'marks': 10,
                },
            },
            {
                'title': 'Forces in structures',
                'minutes': 45,
                'objectives': [
                    'I can describe tension, compression, bending, shear and torsion.',
                    'I can identify the forces acting on members in everyday structures.',
                    'I can explain how structures fail.',
                ],
                'notes': (
                    '<p>When a load is applied, <strong>internal forces</strong> act inside the members of a structure. '
                    'There are five you must know:</p>'
                    '<ul><li><strong>Compression</strong> - pushes inwards and squashes (pillars, table legs).</li>'
                    '<li><strong>Tension</strong> - pulls outwards and stretches (suspension cables, a tow rope).</li>'
                    '<li><strong>Bending</strong> - a load across a member makes one side squash and the other side '
                    'stretch (a plank bridge, a shelf). The top is in compression and the bottom in tension.</li>'
                    '<li><strong>Shear</strong> - two forces act in opposite directions across a member, trying to '
                    'slice it (scissors cutting paper, a bolt holding two plates).</li>'
                    '<li><strong>Torsion</strong> - twisting (turning a screwdriver, wringing out a cloth).</li></ul>'
                    '<p><strong>Structural failure</strong> happens when the forces are too big for the members or joints. '
                    'A structure can <em>buckle</em> (bend under compression), <em>snap</em> or <em>tear</em> (tension), '
                    '<em>topple</em> (it is unstable) or its joints can fail. Engineers design structures with a '
                    '<strong>safety margin</strong> so they can carry more than the expected load.</p>'
                ),
                'key_terms': [
                    ('Bending', 'A force that makes a member curve; one side compresses, the other stretches'),
                    ('Shear', 'Opposite forces that try to slice through a member'),
                    ('Torsion', 'A twisting force'),
                    ('Buckling', 'A member bending sideways and failing under compression'),
                ],
                'example': {
                    'title': 'Class activity: feel the forces',
                    'html': (
                        '<ol><li><strong>Compression:</strong> press a sponge between your palms.</li>'
                        '<li><strong>Tension:</strong> stretch an elastic band.</li>'
                        '<li><strong>Bending:</strong> bend a foam ruler; draw lines on its sides first and see the top '
                        'lines move closer while the bottom lines move apart.</li>'
                        '<li><strong>Shear:</strong> cut paper with scissors.</li>'
                        '<li><strong>Torsion:</strong> twist a wet cloth.</li></ol>'
                        '<p>Record each force with a labelled arrow sketch.</p>'
                    ),
                },
                'video': {'id': 'QrB_6NCRz2I', 'title': 'Grade 8 Technology | Forces in Structures Explained Clearly',
                          'channel': 'Maski', 'minutes': 8},
                'worksheet': {
                    'instructions': 'Name the force and explain your answer.',
                    'exercises': [
                        '1. The chains of a playground swing when a child sits on it.',
                        '2. A shelf loaded with heavy books.',
                        '3. A key being turned in a lock.',
                        '4. The pillars holding up a stadium roof.',
                        '5. A pair of scissors cutting cardboard.',
                        '6. Explain what happens to the top and bottom of a beam under bending.',
                        '7. Give two ways a structure can fail.',
                    ],
                },
                'quiz': [
                    ('mcq', 'Wringing out a wet cloth is an example of:',
                     ['torsion', 'shear', 'tension', 'compression'], 0),
                    ('mcq', 'When a plank bridge bends under a load, the bottom of the plank is in:',
                     ['compression', 'tension', 'torsion', 'shear'], 1),
                    ('tf', 'Scissors cutting paper is an example of shear.', True),
                    ('tf', 'Buckling is a failure caused by tension.', False),
                ],
                'homework': {
                    'title': 'Forces photo diary',
                    'instructions': 'Observe forces in everyday objects.',
                    'tasks': [
                        'Find (sketch or photograph) one example of each of the five forces at home.',
                        'Label each example with the name of the force and an arrow diagram.',
                    ],
                    'marks': 15,
                },
            },
            {
                'title': 'Strengthening frames: triangulation and gussets',
                'minutes': 45,
                'objectives': [
                    'I can explain why triangles make frames rigid.',
                    'I can describe how gussets and cross-bracing strengthen joints.',
                    'I can design and test a strengthened frame model.',
                ],
                'notes': (
                    '<p>A triangle is the only shape that cannot change shape without changing the length of one of '
                    'its sides. That is why engineers use <strong>triangulation</strong> - adding diagonal members '
                    'to divide frames into triangles - to make them <strong>rigid</strong>.</p>'
                    '<ul><li><strong>Cross-bracing</strong>: adding one or two diagonal members across a rectangle '
                    '(you see this on pylons, gates and scaffolding).</li>'
                    '<li><strong>Gussets</strong>: flat triangular plates fixed over a joint to stop it moving. They '
                    'make joints stronger, e.g. on roof trusses and steel bridges.</li>'
                    '<li><strong>Webbing</strong>: a pattern of triangles in a truss, such as the Warren truss used '
                    'in bridges.</li></ul>'
                    '<p>Other ways to strengthen structures:</p>'
                    '<ul><li>Choose stronger materials (steel instead of wood).</li>'
                    '<li>Change the shape of a member: <em>angle iron</em>, I-beams, tubes and corrugated sheets are much '
                    'stronger than flat sheets of the same mass.</li>'
                    '<li>Make the base wider and the centre of gravity lower for <strong>stability</strong>.</li></ul>'
                ),
                'key_terms': [
                    ('Triangulation', 'Using triangles in a frame to make it rigid'),
                    ('Gusset', 'A triangular plate that strengthens a joint'),
                    ('Cross-bracing', 'Diagonal members across a rectangular frame'),
                    ('Rigid', 'Keeps its shape under a load'),
                ],
                'example': {
                    'title': 'Design challenge: the strongest frame',
                    'html': (
                        '<p><strong>Design brief:</strong> Build a 20 cm tall tower frame from 12 straws and tape that '
                        'can hold a 200 g mass without leaning.</p>'
                        '<ol><li>Build a tower with square sides first and test it.</li>'
                        '<li>Add diagonal braces (triangles) to each side and add card gussets at the joints.</li>'
                        '<li>Test again and compare. Record the results in a table.</li>'
                        '<li>Evaluate: which changes made the biggest difference?</li></ol>'
                    ),
                },
                'video': {'id': 'mBHJtWbsiaA', 'title': 'Strong Structures with Triangles | Design Squad',
                          'channel': 'Design Squad ', 'minutes': 3},
                'worksheet': {
                    'instructions': 'Answer the questions and sketch where asked.',
                    'exercises': [
                        '1. Why is a triangle a rigid shape?',
                        '2. What is triangulation? Give two examples where it is used.',
                        '3. Sketch a gate with cross-bracing.',
                        '4. What is a gusset and where would you find one?',
                        '5. Explain why an I-beam is stronger than a flat strip of the same steel.',
                        '6. Give two ways to make a tall tower more stable.',
                    ],
                },
                'quiz': [
                    ('mcq', 'Which shape is the most rigid in a frame?',
                     ['Square', 'Rectangle', 'Triangle', 'Circle'], 2),
                    ('tf', 'A gusset is used to strengthen a joint.', True),
                    ('mcq', 'Adding diagonal members across a rectangle is called:',
                     ['corrugating', 'cross-bracing', 'cladding', 'buckling'], 1),
                    ('tf', 'A narrow base and a high centre of gravity make a structure more stable.', False),
                ],
                'homework': {
                    'title': 'Spot the triangles',
                    'instructions': 'Look for triangulation in real structures.',
                    'tasks': [
                        'Find and sketch three structures that use triangles (bridges, roofs, pylons, cranes, gates).',
                        'For one sketch, explain how the triangles make it stronger.',
                    ],
                    'marks': 10,
                },
            },
        ],
    },

    # ------------------------------------------------------------------ TECH 9
    (9, 'TECH'): {
        'topic': 'Structures: the design process, structural members and graphic communication',
        'caps': 'Technology Gr 9, Term 1: Structures - revision of the design process, structural '
                'members and the forces acting on them, graphic communication (isometric drawing)',
        'summary': 'Learners revise the design process and structural forces, analyse beams and '
                   'columns, and communicate designs with isometric drawings.',
        'days': [
            {
                'title': 'The design process and the design brief',
                'minutes': 50,
                'objectives': [
                    'I can apply the IDMEC design process to a structural problem.',
                    'I can write a design brief with specifications and constraints.',
                    'I can evaluate an existing product against criteria.',
                ],
                'notes': (
                    '<p>In Grade 9 you use the full <strong>design process</strong> (Investigate, Design, Make, Evaluate, '
                    'Communicate) with more independence and detail.</p>'
                    '<p><strong>Investigate:</strong> analyse the problem and existing products. Ask: '
                    '<em>Who</em> is it for? <em>What</em> must it do? <em>Where</em> will it be used? Do a product '
                    'analysis of similar solutions (strength, cost, materials, appearance, safety, environmental impact).</p>'
                    '<p><strong>Design:</strong> write a clear <strong>design brief</strong>, e.g. "Design and make a '
                    'model of a footbridge for learners crossing a 2 m river." Then list:</p>'
                    '<ul><li><strong>Specifications</strong> - measurable requirements (span, load to carry, height above water).</li>'
                    '<li><strong>Constraints</strong> - limits (budget, time, materials, tools, safety rules).</li></ul>'
                    '<p>Generate at least two or three ideas with annotated sketches and choose the best one '
                    'against the specifications.</p>'
                    '<p><strong>Make:</strong> draw up a planning sheet and a list of materials and tools. '
                    '<strong>Evaluate:</strong> test the model with a load and decide how to improve it. '
                    '<strong>Communicate:</strong> present the solution with working drawings and a short report.</p>'
                    '<p>Good design also considers <strong>bias</strong> and impact: who benefits and who might be '
                    'left out or harmed?</p>'
                ),
                'key_terms': [
                    ('Design brief', 'A clear statement of the problem and what will be made'),
                    ('Specification', 'A measurable requirement the solution must meet'),
                    ('Constraint', 'A limit on the solution, such as cost or time'),
                    ('Product analysis', 'Evaluating existing products against criteria'),
                ],
                'example': {
                    'title': 'Worked example: from scenario to brief',
                    'html': (
                        '<p><strong>Scenario:</strong> A community vegetable garden needs a raised water tank so water '
                        'can flow to the beds by gravity.</p>'
                        '<p><strong>Design brief:</strong> Design and make a 1:20 scale model of a stand for a 1 000 L water tank.</p>'
                        '<p><strong>Specifications:</strong> stand is 2 m high (10 cm on the model); model must hold a 1 kg mass; '
                        'must not topple; uses triangulation.</p>'
                        '<p><strong>Constraints:</strong> sosatie sticks, glue and card only; complete in two weeks.</p>'
                    ),
                },
                'video': {'id': 'a6IS6vQ4wJc', 'title': 'Grade 9 | Design Brief | Term 1 | Week 5 | Lesson 1 | Technology',
                          'channel': 'Leruo Learning', 'minutes': 10},
                'worksheet': {
                    'instructions': 'Read the scenario and complete the tasks.',
                    'exercises': [
                        'Scenario: Taxi commuters wait in the rain at a busy rank with no shelter.',
                        '1. Write three investigation questions you would ask.',
                        '2. Write a design brief for a solution.',
                        '3. List four specifications.',
                        '4. List three constraints.',
                        '5. Name two existing shelters and give one strength and one weakness of each.',
                        '6. How could your design be unfair to some users (e.g. elderly or disabled people)? How would you avoid this?',
                    ],
                },
                'quiz': [
                    ('mcq', '"The model must hold a 2 kg load" is an example of a:',
                     ['constraint', 'specification', 'design brief', 'product analysis'], 1),
                    ('mcq', 'In which step do you test the product and suggest improvements?',
                     ['Investigate', 'Make', 'Evaluate', 'Design'], 2),
                    ('tf', 'A limited budget is an example of a constraint.', True),
                    ('tf', 'A design brief is a detailed list of tools needed to make the product.', False),
                ],
                'homework': {
                    'title': 'Product analysis',
                    'instructions': 'Choose a structure at home (a chair, a shelf, a ladder or a gate).',
                    'tasks': [
                        'Describe its purpose, materials and the type of structure it is.',
                        'Evaluate it for strength, stability, safety and appearance.',
                        'Suggest one improvement and explain why it would help.',
                    ],
                    'marks': 15,
                },
            },
            {
                'title': 'Structural members: beams, columns and the forces in them',
                'minutes': 50,
                'objectives': [
                    'I can identify beams, columns, struts and ties in a structure.',
                    'I can explain how beams resist bending and why I-beams are efficient.',
                    'I can show forces in members with arrow diagrams.',
                ],
                'notes': (
                    '<p>Structures are built from <strong>members</strong>, each carrying certain forces:</p>'
                    '<ul><li><strong>Columns</strong> - vertical members in compression that carry loads down to the '
                    'foundations. Long, thin columns can <em>buckle</em>.</li>'
                    '<li><strong>Beams</strong> - horizontal members that span a gap and resist <strong>bending</strong>. '
                    'When a beam bends, the top is in compression and the bottom is in tension. The middle '
                    '(the <em>neutral axis</em>) has almost no force.</li>'
                    '<li><strong>Struts</strong> (compression) and <strong>ties</strong> (tension) in frames and trusses.</li></ul>'
                    '<p>Because the middle of a beam does little work, engineers remove material there. An '
                    '<strong>I-beam</strong> (or H-section) puts most of the material in the top and bottom '
                    '<em>flanges</em>, joined by a thin <em>web</em>. It is nearly as strong as a solid beam but '
                    'much lighter and cheaper. A <strong>girder</strong> is a large beam, often made as an I-beam '
                    'or a truss, used in bridges and buildings.</p>'
                    '<p>Also remember <strong>shear</strong> (slicing forces at supports and bolts) and '
                    '<strong>torsion</strong> (twisting). Making a beam <em>deeper</em> (taller) increases its '
                    'resistance to bending far more than making it wider.</p>'
                ),
                'key_terms': [
                    ('Beam', 'A horizontal member that spans a gap and resists bending'),
                    ('Column', 'A vertical member in compression'),
                    ('I-beam', 'A beam with flanges and a web, strong but light'),
                    ('Girder', 'A large main beam in a bridge or building'),
                    ('Neutral axis', 'The line inside a bent beam with almost no stress'),
                ],
                'example': {
                    'title': 'Class investigation: deep or wide?',
                    'html': (
                        '<ol><li>Place a 30 cm ruler flat across two stacks of books and hang a small bag of coins in the middle. '
                        'Measure how far it sags.</li>'
                        '<li>Turn the same ruler on its edge (deep) and repeat.</li>'
                        '<li>Compare: on its edge, the ruler sags much less, because depth resists bending.</li>'
                        '<li>Link it to I-beams and floor joists, which are always placed on their edge.</li></ol>'
                    ),
                },
                'video': {'id': 'oQDDNqALQ1o', 'title': 'Structural Forces Explained: Tension, Compression, Bending, Shear & Torsion',
                          'channel': 'Ruslan Engineering', 'minutes': 8},
                'worksheet': {
                    'instructions': 'Answer the questions; use arrow diagrams where asked.',
                    'exercises': [
                        '1. What is the difference between a beam and a column?',
                        '2. Draw a loaded beam on two supports. Show which part is in tension and which in compression.',
                        '3. Why do long, thin columns tend to buckle?',
                        '4. Explain why an I-beam is efficient.',
                        '5. Why are floor joists placed on their narrow edge?',
                        '6. Name the force acting on a bolt that holds two steel plates together when they are pulled apart sideways.',
                    ],
                },
                'quiz': [
                    ('mcq', 'In a beam loaded from above, the bottom edge is in:',
                     ['compression', 'torsion', 'tension', 'no force'], 2),
                    ('tf', 'An I-beam puts most of its material in the flanges, far from the neutral axis.', True),
                    ('mcq', 'Which change increases a beam\'s resistance to bending the most?',
                     ['Making it deeper (taller)', 'Painting it', 'Making it longer', 'Making it thinner'], 0),
                    ('tf', 'Columns are mainly in tension.', False),
                ],
                'homework': {
                    'title': 'Beams in buildings',
                    'instructions': 'Look at a building, bridge or carport near you.',
                    'tasks': [
                        'Sketch the structure and label at least two beams and two columns.',
                        'Add arrows to show the forces in one beam and one column.',
                    ],
                    'marks': 10,
                },
            },
            {
                'title': 'Graphic communication: isometric drawing',
                'minutes': 50,
                'objectives': [
                    'I can draw a simple object in isometric projection.',
                    'I can use isometric grid paper or 30° lines correctly.',
                    'I can explain when isometric drawings are used.',
                ],
                'notes': (
                    '<p>Designers communicate ideas with drawings. An <strong>isometric drawing</strong> shows an object '
                    'in 3D, with three faces visible, in a way that keeps measurements true along the three main axes.</p>'
                    '<p><strong>Rules for isometric drawing:</strong></p>'
                    '<ul><li>Vertical edges stay <strong>vertical</strong>.</li>'
                    '<li>Horizontal edges are drawn at <strong>30°</strong> to the horizontal, to the left and right.</li>'
                    '<li>All lines that are parallel on the object are parallel on the drawing.</li>'
                    '<li>Measurements along the three axes are drawn true length (or to scale).</li></ul>'
                    '<p><strong>Steps to draw a box 60 x 40 x 30 mm:</strong></p>'
                    '<ol><li>Draw the front vertical corner edge (30 mm).</li>'
                    '<li>From the bottom of it, draw a 60 mm line at 30° to the right and a 40 mm line at 30° to the left.</li>'
                    '<li>Draw vertical lines (30 mm) up from the ends of these lines.</li>'
                    '<li>Join the tops with lines parallel to the bottom lines to complete the top face.</li>'
                    '<li>Darken the outline; leave construction lines light.</li></ol>'
                    '<p>Isometric grid paper (dots or lines at 30°) makes this easier. Isometric drawings are used for '
                    'presenting designs, instructions and assembly diagrams. <strong>Oblique</strong> drawing is a '
                    'simpler alternative where the front face is drawn flat and depth lines go back at 45°.</p>'
                ),
                'key_terms': [
                    ('Isometric drawing', 'A 3D drawing with horizontal edges at 30°'),
                    ('Oblique drawing', 'A 3D drawing with a flat front face and depth at 45°'),
                    ('Construction lines', 'Light guide lines used while drawing'),
                    ('Isometric grid', 'Paper with dots or lines at 30° to help isometric drawing'),
                ],
                'example': {
                    'title': 'Guided drawing: an L-shaped block',
                    'html': (
                        '<p>On isometric dot paper:</p>'
                        '<ol><li>Draw a box 4 dots long, 2 dots deep and 3 dots high, using light lines.</li>'
                        '<li>Cut away a block 2 dots long and 2 dots high from the top right to form an "L".</li>'
                        '<li>Rub out the lines that are no longer visible and darken the final outline.</li>'
                        '<li>Shade the top faces lightly, the left faces medium and the right faces darker to show depth.</li></ol>'
                    ),
                },
                'video': {'id': 'WhSJDrp4eOE', 'title': 'Introduction to Isometric Drawing',
                          'channel': 'Nathan Nagele', 'minutes': 8},
                'worksheet': {
                    'instructions': 'Use isometric grid paper, a sharp pencil and a ruler.',
                    'exercises': [
                        '1. At what angle are horizontal edges drawn in isometric drawing?',
                        '2. Draw a cube with 40 mm sides in isometric.',
                        '3. Draw a box 60 mm long, 30 mm wide and 20 mm high in isometric.',
                        '4. Draw the same box in oblique projection.',
                        '5. Give one advantage of isometric drawing over oblique drawing.',
                        '6. Draw your water tank stand idea from Day 1 in isometric.',
                    ],
                },
                'quiz': [
                    ('mcq', 'In isometric drawing, horizontal edges are drawn at:',
                     ['45°', '90°', '30°', '60°'], 2),
                    ('tf', 'Vertical edges remain vertical in an isometric drawing.', True),
                    ('mcq', 'In oblique drawing, depth lines are usually drawn at:',
                     ['30°', '45°', '90°', '15°'], 1),
                    ('tf', 'Construction lines should be drawn darker than the final outline.', False),
                ],
                'homework': {
                    'title': 'Draw it in 3D',
                    'instructions': 'Choose a simple box-shaped object at home (a cereal box, a brick, a book).',
                    'tasks': [
                        'Measure the object and draw it in isometric projection at a suitable scale.',
                        'Add dimensions to three edges and shade the faces to show depth.',
                    ],
                    'marks': 15,
                },
            },
        ],
    },

    # ------------------------------------------------------------------ EMS 7
    (7, 'EMS'): {
        'topic': 'The economy: History of money',
        'caps': 'EMS Gr 7, Term 1, The economy: History of money - traditional societies, '
                'bartering, the use of coins and notes, and electronic money/banking',
        'summary': 'Learners trace how people moved from bartering to commodity money, coins and '
                   'notes, and today\'s electronic money, and identify the features of good money.',
        'days': [
            {
                'title': 'Traditional societies and bartering',
                'minutes': 40,
                'objectives': [
                    'I can explain how traditional societies met their needs.',
                    'I can define bartering and give examples.',
                    'I can explain the problems with bartering.',
                ],
                'notes': (
                    '<p>Long ago, people in <strong>traditional societies</strong> lived in small groups and produced '
                    'most of what they needed themselves: they hunted, gathered plants, farmed crops and kept '
                    'livestock. This is called <strong>subsistence</strong> living.</p>'
                    '<p>When a family had more of something than it needed (a <em>surplus</em>), it could swap it '
                    'for goods it did not have. Exchanging goods or services directly, without money, is called '
                    '<strong>bartering</strong>. For example, a farmer might swap a bag of maize for a clay pot.</p>'
                    '<p><strong>Problems with bartering:</strong></p>'
                    '<ul><li><strong>Double coincidence of wants:</strong> you must find someone who has what you want '
                    '<em>and</em> wants what you have.</li>'
                    '<li><strong>Value:</strong> it is hard to agree how many chickens equal one cow.</li>'
                    '<li><strong>Divisibility:</strong> you cannot cut a cow in half to buy something small.</li>'
                    '<li><strong>Storage:</strong> food goods can rot, and animals must be fed.</li>'
                    '<li><strong>Carrying:</strong> large goods are hard to transport to trade.</li></ul>'
                    '<p>Because of these problems, people began to use goods that everyone accepted as a '
                    '<strong>medium of exchange</strong>.</p>'
                ),
                'key_terms': [
                    ('Bartering', 'Exchanging goods or services directly without money'),
                    ('Subsistence', 'Producing only enough to meet your own needs'),
                    ('Surplus', 'More than is needed'),
                    ('Double coincidence of wants', 'Each trader wants what the other has'),
                ],
                'example': {
                    'title': 'Class activity: the barter market',
                    'html': (
                        '<p>Give each learner a card showing a good (3 chickens, a blanket, a bag of maize, a goat, '
                        'a clay pot, a basket of fish) and a card showing what they want.</p>'
                        '<ol><li>Learners have five minutes to trade only by bartering.</li>'
                        '<li>Who got what they wanted? Who could not trade? Why not?</li>'
                        '<li>Discuss the problems learners experienced and link them to the notes.</li></ol>'
                    ),
                },
                'video': {'id': 'GZ7y-yFdX9M',
                          'title': 'Who Invented Money? | The History of Money | Barter System of Exchange | The Dr Binocs Show',
                          'channel': 'Peekaboo Kidz', 'minutes': 5},
                'worksheet': {
                    'instructions': 'Answer the questions in full sentences.',
                    'exercises': [
                        '1. How did traditional societies get the things they needed?',
                        '2. Define bartering.',
                        '3. Give an example of a barter trade.',
                        '4. Explain the "double coincidence of wants" in your own words.',
                        '5. Why is it difficult to barter a cow for a loaf of bread?',
                        '6. Name two other problems with bartering.',
                    ],
                },
                'quiz': [
                    ('mcq', 'Exchanging goods directly without using money is called:',
                     ['saving', 'bartering', 'banking', 'borrowing'], 1),
                    ('tf', 'In bartering, you need someone who wants what you have and has what you want.', True),
                    ('mcq', 'Which is a problem with bartering?',
                     ['Goods are easy to divide', 'Values are easy to agree on',
                      'Some goods rot or are hard to store', 'Everyone always wants the same goods'], 2),
                ],
                'homework': {
                    'title': 'Bartering in my family',
                    'instructions': 'Talk to an older family member.',
                    'tasks': [
                        'Ask whether they ever swapped goods or services instead of using money. Write down their story.',
                        'List three things you could barter today and what you would want in exchange.',
                    ],
                    'marks': 10,
                },
            },
            {
                'title': 'From commodity money to coins and notes',
                'minutes': 40,
                'objectives': [
                    'I can give examples of commodity money used in the past.',
                    'I can explain why coins and notes were introduced.',
                    'I can list the characteristics of good money.',
                ],
                'notes': (
                    '<p>To solve the problems of bartering, people began to use items that everyone valued and '
                    'accepted. This is called <strong>commodity money</strong>. Examples: cattle in southern Africa, '
                    'salt in West Africa and Rome, cowrie shells in Africa and Asia, beads, copper and iron.</p>'
                    '<p>Later, people used precious metals like gold and silver. Over 2 500 years ago, rulers in '
                    'Lydia (modern Turkey) stamped metal pieces to show their value: the first <strong>coins</strong>. '
                    'The Chinese were the first to use <strong>paper money</strong>, because heavy coins were hard '
                    'to carry. Today South Africa\'s currency is the <strong>rand</strong> (R), issued by the '
                    '<strong>South African Reserve Bank</strong>.</p>'
                    '<p><strong>Characteristics of good money:</strong></p>'
                    '<ul><li><strong>Acceptable</strong> - everyone agrees to use it.</li>'
                    '<li><strong>Durable</strong> - it lasts and does not rot.</li>'
                    '<li><strong>Portable</strong> - easy to carry.</li>'
                    '<li><strong>Divisible</strong> - can be split into smaller amounts (R1 = 100 cents).</li>'
                    '<li><strong>Scarce / limited supply</strong> - so it keeps its value.</li>'
                    '<li><strong>Difficult to forge</strong> - security features such as watermarks.</li></ul>'
                    '<p>Money works as a <em>medium of exchange</em>, a <em>measure of value</em> (prices) and a '
                    '<em>store of value</em> (you can save it).</p>'
                ),
                'key_terms': [
                    ('Commodity money', 'A useful item accepted as payment, e.g. cattle or salt'),
                    ('Currency', 'The money used in a country, e.g. the rand'),
                    ('Medium of exchange', 'Something accepted in exchange for goods and services'),
                    ('Durable', 'Long-lasting'),
                    ('Divisible', 'Can be split into smaller units'),
                ],
                'example': {
                    'title': 'Guided activity: is it good money?',
                    'html': (
                        '<p>Test each item against the characteristics of good money: <em>a cow, a bag of salt, '
                        'a R50 note, a tomato, a gold coin</em>.</p>'
                        '<p>For example, a <strong>tomato</strong>: not durable (rots), not easily divisible, not scarce. '
                        'Poor money!</p>'
                        '<p>A <strong>R50 note</strong>: acceptable, portable, durable, divisible into coins, '
                        'hard to forge. Good money.</p>'
                    ),
                },
                'video': {'id': 'fcrQHC3jRsA',
                          'title': 'The History of Money: From Bartering to Banknotes 💰 Economy for Kids | @HappyLearningENG',
                          'channel': 'Happy Learning English', 'minutes': 4},
                'worksheet': {
                    'instructions': 'Use your notes to answer.',
                    'exercises': [
                        '1. What is commodity money? Give three examples.',
                        '2. Why were cattle not ideal as money?',
                        '3. Why did people start using paper money?',
                        '4. Name South Africa\'s currency and the institution that issues it.',
                        '5. List five characteristics of good money.',
                        '6. Explain how money is a "store of value".',
                    ],
                },
                'quiz': [
                    ('mcq', 'Which was used as commodity money in Africa?',
                     ['Cowrie shells', 'Credit cards', 'Cheques', 'Bitcoin'], 0),
                    ('mcq', 'Which characteristic means money is easy to carry?',
                     ['Durable', 'Divisible', 'Portable', 'Scarce'], 2),
                    ('tf', 'The South African Reserve Bank issues the rand.', True),
                    ('tf', 'Good money should be easy to forge.', False),
                ],
                'homework': {
                    'title': 'Look closely at a banknote',
                    'instructions': 'Use any South African banknote or coin (or a picture of one).',
                    'tasks': [
                        'Describe what is shown on the front and back.',
                        'Find and list three security features on a banknote.',
                        'Explain which characteristics of good money the note has.',
                    ],
                    'marks': 12,
                },
            },
            {
                'title': 'Money today: electronic banking and cards',
                'minutes': 40,
                'objectives': [
                    'I can describe forms of electronic money and payment.',
                    'I can explain advantages and disadvantages of electronic banking.',
                    'I can identify ways to keep money safe from fraud.',
                ],
                'notes': (
                    '<p>Today much of our money is not cash. It is stored as numbers in bank accounts and moved '
                    'electronically. This is <strong>electronic money</strong>.</p>'
                    '<ul><li><strong>Debit card</strong> - takes money straight from your own bank account.</li>'
                    '<li><strong>Credit card</strong> - lets you borrow money from the bank to pay later, usually '
                    'with interest if you do not pay on time.</li>'
                    '<li><strong>EFT (electronic funds transfer)</strong> - moves money from one account to another, '
                    'often through internet or cellphone banking.</li>'
                    '<li><strong>Tap-to-pay and mobile wallets</strong> - pay with a card or phone at a card machine.</li>'
                    '<li><strong>ATMs</strong> - machines where you can draw cash and check your balance.</li></ul>'
                    '<p><strong>Advantages:</strong> safer than carrying lots of cash, fast, can pay any time and '
                    'from anywhere, keeps a record of payments.</p>'
                    '<p><strong>Disadvantages:</strong> bank fees, needs electricity, network and a device, risk of '
                    '<em>fraud</em> and scams, and it is easier to overspend.</p>'
                    '<p><strong>Stay safe:</strong> never share your PIN or one-time password (OTP), cover the keypad '
                    'at an ATM, and do not click links in suspicious messages.</p>'
                ),
                'key_terms': [
                    ('Electronic money', 'Money stored and moved electronically, not as cash'),
                    ('Debit card', 'A card that uses money in your own account'),
                    ('Credit card', 'A card that lets you borrow money to pay later'),
                    ('EFT', 'Electronic funds transfer between accounts'),
                    ('PIN', 'A secret personal identification number'),
                ],
                'example': {
                    'title': 'Class activity: timeline of money',
                    'html': (
                        '<p>In groups, create a timeline on a strip of paper with these stages in order:</p>'
                        '<ol><li>Subsistence living</li><li>Bartering</li><li>Commodity money (cattle, salt, shells)</li>'
                        '<li>Metal coins</li><li>Paper money</li><li>Cheques and bank accounts</li>'
                        '<li>Cards and ATMs</li><li>Cellphone banking and mobile wallets</li></ol>'
                        '<p>Add a picture and one sentence for each stage. Discuss: what might money look like in 50 years?</p>'
                    ),
                },
                'video': {'id': 'RGQCzVgmZrs', 'title': 'The History of Money: Barter, Fiat and Bitcoin',
                          'channel': 'Sprouts', 'minutes': 6},
                'worksheet': {
                    'instructions': 'Answer the questions.',
                    'exercises': [
                        '1. What is electronic money?',
                        '2. What is the difference between a debit card and a credit card?',
                        '3. What does EFT stand for?',
                        '4. Give two advantages of electronic banking.',
                        '5. Give two disadvantages of electronic banking.',
                        '6. List three ways to protect yourself from banking fraud.',
                    ],
                },
                'quiz': [
                    ('mcq', 'A card that takes money directly from your own account is a:',
                     ['credit card', 'loyalty card', 'debit card', 'gift voucher'], 2),
                    ('tf', 'You should never share your PIN or OTP with anyone.', True),
                    ('mcq', 'Which came FIRST in the history of money?',
                     ['Paper notes', 'Bartering', 'Coins', 'Debit cards'], 1),
                    ('tf', 'Electronic banking works without electricity or a network.', False),
                ],
                'homework': {
                    'title': 'How does my family pay?',
                    'instructions': 'Ask an adult at home about the ways they pay for things.',
                    'tasks': [
                        'List the methods of payment your household uses (cash, card, EFT, etc.).',
                        'For one method, write one advantage and one disadvantage.',
                        'Design a short poster with three tips to avoid banking scams.',
                    ],
                    'marks': 15,
                },
            },
        ],
    },

    # ------------------------------------------------------------------ EMS 8
    (8, 'EMS'): {
        'topic': 'The economy: Government',
        'caps': 'EMS Gr 8, Term 1, The economy: Government - meaning of government, the three '
                'levels (spheres) of government in South Africa and their roles in respect of '
                'households and businesses, government revenue',
        'summary': 'Learners define government, study the national, provincial and local spheres '
                   'and their roles, and see how government raises the money it spends.',
        'days': [
            {
                'title': 'What is government? The three spheres',
                'minutes': 45,
                'objectives': [
                    'I can explain the meaning of government.',
                    'I can name the three spheres of government in South Africa.',
                    'I can describe the three arms (branches) of government.',
                ],
                'notes': (
                    '<p>A <strong>government</strong> is the group of people and institutions with the authority to '
                    'make laws, run the country and provide public goods and services for its citizens. In South Africa, '
                    'the <strong>Constitution</strong> (1996) is the highest law and sets out how government works.</p>'
                    '<p>South Africa has <strong>three spheres (levels) of government</strong>:</p>'
                    '<ul><li><strong>National government</strong> - led by the President and Cabinet; Parliament in '
                    'Cape Town makes laws for the whole country.</li>'
                    '<li><strong>Provincial government</strong> - nine provinces, each led by a Premier and a '
                    'provincial legislature.</li>'
                    '<li><strong>Local government</strong> - municipalities (metropolitan, district and local), led by '
                    'mayors and councillors elected by communities.</li></ul>'
                    '<p>Power is also divided into <strong>three arms</strong> so that no one group has all the power '
                    '(<em>separation of powers</em>):</p>'
                    '<ul><li><strong>Legislature</strong> - makes laws (Parliament).</li>'
                    '<li><strong>Executive</strong> - carries out laws and runs government departments (President and Cabinet).</li>'
                    '<li><strong>Judiciary</strong> - the courts, which interpret the law and settle disputes.</li></ul>'
                ),
                'key_terms': [
                    ('Government', 'The institutions that make laws and run the country'),
                    ('Constitution', 'The highest law of South Africa'),
                    ('Municipality', 'Local government for a city, town or area'),
                    ('Separation of powers', 'Dividing power between legislature, executive and judiciary'),
                ],
                'example': {
                    'title': 'Class activity: who is in charge?',
                    'html': (
                        '<p>Draw a three-level diagram on the board: National at the top, Provincial in the middle and '
                        'Local at the bottom.</p>'
                        '<ol><li>Learners name the leader of each sphere (President, Premier, Mayor).</li>'
                        '<li>Learners name their own province and municipality.</li>'
                        '<li>Discuss: why does a big country need more than one level of government?</li></ol>'
                    ),
                },
                'video': {'id': 'O-An-rF_goo', 'title': 'Levels of government - A Grade 8 Economics& Management Sciences topic',
                          'channel': 'SimplifyingSchool', 'minutes': 6},
                'worksheet': {
                    'instructions': 'Answer the questions.',
                    'exercises': [
                        '1. Define government.',
                        '2. Name the three spheres of government in South Africa.',
                        '3. Who leads each sphere?',
                        '4. How many provinces does South Africa have? Name your province.',
                        '5. Name the three arms of government and the role of each.',
                        '6. Why is the separation of powers important?',
                    ],
                },
                'quiz': [
                    ('mcq', 'Which sphere of government is led by a Premier?',
                     ['National', 'Provincial', 'Local', 'Judicial'], 1),
                    ('mcq', 'Which arm of government interprets the law?',
                     ['The judiciary', 'The legislature', 'The executive', 'The municipality'], 0),
                    ('tf', 'South Africa has nine provinces.', True),
                    ('tf', 'Local government is led by the President.', False),
                ],
                'homework': {
                    'title': 'My government',
                    'instructions': 'Use the news, the internet or ask an adult.',
                    'tasks': [
                        'Name the current President, the Premier of your province and your municipality.',
                        'Find one news story about a government service and say which sphere is responsible.',
                    ],
                    'marks': 10,
                },
            },
            {
                'title': 'Roles of the spheres for households and businesses',
                'minutes': 45,
                'objectives': [
                    'I can describe the roles of national, provincial and local government.',
                    'I can match services to the sphere responsible for them.',
                    'I can explain how government services affect households and businesses.',
                ],
                'notes': (
                    '<p>Each sphere provides different goods and services:</p>'
                    '<ul><li><strong>National government:</strong> defence (army), foreign affairs, national roads, '
                    'the police service, home affairs (IDs, passports), social grants (through SASSA), the national '
                    'budget, tax collection (SARS) and laws on trade and business.</li>'
                    '<li><strong>Provincial government:</strong> schools and education departments, hospitals and '
                    'clinics, provincial roads, housing and agriculture in the province.</li>'
                    '<li><strong>Local government (municipalities):</strong> water and sanitation, electricity '
                    'distribution, refuse removal, local roads and streetlights, parks, libraries, building plans '
                    'and business licences.</li></ul>'
                    '<p><strong>Households</strong> benefit from free or subsidised services such as schools, clinics, '
                    'grants and clean water. <strong>Businesses</strong> need roads, electricity, water, safety and '
                    'clear laws to produce and sell goods. Government also <em>regulates</em> businesses (e.g. health '
                    'and safety rules, minimum wages) and buys goods from them.</p>'
                    '<p>Government uses the country\'s scarce <strong>resources</strong> (money, land, workers) and must '
                    'choose how to use them fairly and efficiently.</p>'
                ),
                'key_terms': [
                    ('Public goods and services', 'Goods and services provided by government for everyone'),
                    ('SASSA', 'South African Social Security Agency, pays social grants'),
                    ('SARS', 'South African Revenue Service, collects taxes'),
                    ('Regulate', 'To control with rules and laws'),
                ],
                'example': {
                    'title': 'Guided activity: which sphere?',
                    'html': (
                        '<p>Sort these into national, provincial or local:</p>'
                        '<p><em>Issuing passports, collecting rubbish, running a public hospital, paying the child '
                        'support grant, fixing a streetlight, the army, building a provincial school.</em></p>'
                        '<p><strong>Answers:</strong> National - passports, child support grant, army. '
                        'Provincial - public hospital, provincial school. Local - rubbish, streetlight.</p>'
                    ),
                },
                'video': {'id': 'LPX9GHnAqRI', 'title': 'Gr8 EMS: Eco. & Entr. | Term 1 | Lesson 1 | The Government  (Part 1)',
                          'channel': 'Thuma Mina Teaching', 'minutes': 10},
                'worksheet': {
                    'instructions': 'Answer in full sentences.',
                    'exercises': [
                        '1. Name three services provided by national government.',
                        '2. Name two services provided by provincial government.',
                        '3. Name three services provided by your municipality.',
                        '4. Which sphere is responsible for public schools?',
                        '5. Explain two ways government services help businesses.',
                        '6. Explain two ways government services help households.',
                    ],
                },
                'quiz': [
                    ('mcq', 'Refuse (rubbish) removal is the responsibility of:',
                     ['national government', 'provincial government', 'local government', 'the courts'], 2),
                    ('mcq', 'Which sphere is responsible for defence (the army)?',
                     ['National', 'Provincial', 'Local', 'All three equally'], 0),
                    ('tf', 'Provincial government runs public hospitals and schools.', True),
                    ('tf', 'Municipalities issue passports.', False),
                ],
                'homework': {
                    'title': 'Services in my community',
                    'instructions': 'Walk around your area or think about your household.',
                    'tasks': [
                        'List six government services your household uses.',
                        'Next to each, write which sphere of government provides it.',
                        'Choose one service that could be improved and suggest how.',
                    ],
                    'marks': 12,
                },
            },
            {
                'title': 'Where does government get its money?',
                'minutes': 45,
                'objectives': [
                    'I can identify sources of government revenue.',
                    'I can explain the difference between direct and indirect taxes.',
                    'I can calculate VAT on a simple purchase.',
                ],
                'notes': (
                    '<p>Government needs money (<strong>revenue</strong>) to pay for services. Its main source is '
                    '<strong>taxes</strong>, collected by the <strong>South African Revenue Service (SARS)</strong>.</p>'
                    '<p><strong>Direct taxes</strong> are paid directly to SARS by the person or business that earns the income:</p>'
                    '<ul><li><strong>Personal income tax</strong> - on salaries and wages (higher earners pay a higher rate).</li>'
                    '<li><strong>Company tax</strong> - on business profits.</li></ul>'
                    '<p><strong>Indirect taxes</strong> are added to the price of goods and services, so everyone who buys pays them:</p>'
                    '<ul><li><strong>Value-added tax (VAT)</strong> - 15% on most goods and services. Some basic foods '
                    '(e.g. brown bread, maize meal, milk, eggs) are zero-rated.</li>'
                    '<li><strong>Excise duties</strong> - extra tax on items like alcohol, tobacco and fuel.</li>'
                    '<li><strong>Customs duties</strong> - on imported goods.</li></ul>'
                    '<p>Other revenue: fees and fines, and municipal <strong>rates</strong> and service charges '
                    'paid to local government. When government spends more than it collects, it must '
                    '<em>borrow</em>. The national plan of revenue and spending is the <strong>national budget</strong>, '
                    'presented every February by the Minister of Finance.</p>'
                ),
                'key_terms': [
                    ('Revenue', 'Income received by government'),
                    ('Direct tax', 'Tax paid directly on income or profit'),
                    ('Indirect tax', 'Tax included in the price of goods and services'),
                    ('VAT', 'Value-added tax, 15% in South Africa'),
                    ('National budget', 'Government\'s yearly plan of income and spending'),
                ],
                'example': {
                    'title': 'Worked example: calculating VAT',
                    'html': (
                        '<p>A pair of school shoes costs <strong>R400 excluding VAT</strong>.</p>'
                        '<p>VAT = 15% x R400 = 0,15 x R400 = <strong>R60</strong></p>'
                        '<p>Price including VAT = R400 + R60 = <strong>R460</strong></p>'
                        '<p>The shop pays the R60 VAT over to SARS. VAT is an <em>indirect</em> tax because the buyer '
                        'pays it through the price, not directly to SARS.</p>'
                    ),
                },
                'video': {'id': 'uuvupHhZ6BU', 'title': 'NATIONAL BUDGET - Government Income and Expenses - Part 1',
                          'channel': 'SHFT - Your Learning', 'minutes': 8},
                'worksheet': {
                    'instructions': 'Answer the questions and show calculations.',
                    'exercises': [
                        '1. What is government revenue?',
                        '2. Which organisation collects taxes in South Africa?',
                        '3. Classify as direct or indirect: VAT, personal income tax, company tax, fuel levy.',
                        '4. Calculate the VAT on a R200 item (excluding VAT) and the price including VAT.',
                        '5. Why are some basic foods zero-rated for VAT?',
                        '6. What does government do if it spends more than it collects?',
                    ],
                },
                'quiz': [
                    ('mcq', 'Which of these is a direct tax?',
                     ['VAT', 'Customs duty', 'Personal income tax', 'Excise duty'], 2),
                    ('mcq', 'What is 15% VAT on R100?', ['R1,50', 'R15', 'R115', 'R85'], 1),
                    ('tf', 'Indirect taxes are included in the price of goods and services.', True),
                    ('tf', 'Only people who earn a salary pay VAT.', False),
                ],
                'homework': {
                    'title': 'Spot the VAT',
                    'instructions': 'Look at a till slip from a shop (ask an adult).',
                    'tasks': [
                        'Find the total, the VAT amount and any zero-rated items on the slip.',
                        'Check the VAT: is it about 15/115 of the total of the VAT-able items?',
                        'Explain in two sentences why paying taxes is important.',
                    ],
                    'marks': 10,
                },
            },
        ],
    },

    # ------------------------------------------------------------------ EMS 9
    (9, 'EMS'): {
        'topic': 'The economy: Economic systems',
        'caps': 'EMS Gr 9, Term 1, The economy: Economic systems - the basic economic problem, '
                'traditional, market (free-market), command (centrally planned) and mixed economies',
        'summary': 'Learners revisit the economic problem of scarcity and compare how traditional, '
                   'market, command and mixed economic systems answer the basic economic questions.',
        'days': [
            {
                'title': 'The economic problem and traditional economies',
                'minutes': 45,
                'objectives': [
                    'I can explain the basic economic problem of scarcity.',
                    'I can state the three economic questions every society must answer.',
                    'I can describe the features of a traditional economy.',
                ],
                'notes': (
                    '<p>People have <strong>unlimited wants</strong>, but the resources to satisfy them (natural resources, '
                    'labour, capital and entrepreneurship) are <strong>limited</strong>. This is the basic economic problem: '
                    '<strong>scarcity</strong>. Because of scarcity, every society must make choices, and every choice has '
                    'an <em>opportunity cost</em> (the next-best alternative given up).</p>'
                    '<p>Every society must answer three <strong>economic questions</strong>:</p>'
                    '<ol><li><strong>What</strong> to produce? (which goods and services, and how much)</li>'
                    '<li><strong>How</strong> to produce? (which resources and methods)</li>'
                    '<li><strong>For whom</strong> to produce? (who gets the goods and services)</li></ol>'
                    '<p>An <strong>economic system</strong> is the way a society organises production and distribution '
                    'to answer these questions.</p>'
                    '<p>In a <strong>traditional economy</strong>, the questions are answered by <em>custom and tradition</em>. '
                    'People produce what their parents produced (e.g. herding, subsistence farming, fishing), using '
                    'skills passed down through generations. Goods are shared according to custom, and barter is common. '
                    'Advantages: stable, clear roles, close communities, little waste. Disadvantages: slow progress, few '
                    'choices, vulnerable to droughts and disasters. Traditional elements still exist in rural parts of '
                    'Africa and among groups such as the San.</p>'
                ),
                'key_terms': [
                    ('Scarcity', 'Limited resources compared to unlimited wants'),
                    ('Opportunity cost', 'The next-best alternative given up when you choose'),
                    ('Economic system', 'How a society decides what, how and for whom to produce'),
                    ('Traditional economy', 'An economy based on custom and tradition'),
                ],
                'example': {
                    'title': 'Worked example: opportunity cost',
                    'html': (
                        '<p>Thabo has R150. He can buy a new cricket bat <em>or</em> a ticket to a soccer match. '
                        'He chooses the bat.</p>'
                        '<p>The <strong>opportunity cost</strong> of the bat is the soccer match he gave up.</p>'
                        '<p>A country faces the same problem: if it spends more on building roads, it may have less '
                        'to spend on new schools. The economic system shapes who makes these choices.</p>'
                    ),
                },
                'video': {'id': '5vTdPNY7P2w', 'title': 'The 4 Types of Economies | Economics Concepts Explained | Think Econ',
                          'channel': 'Think Econ', 'minutes': 6},
                'worksheet': {
                    'instructions': 'Answer the questions.',
                    'exercises': [
                        '1. Explain the basic economic problem.',
                        '2. Name the four factors of production.',
                        '3. List the three economic questions.',
                        '4. Define opportunity cost and give your own example.',
                        '5. How are the economic questions answered in a traditional economy?',
                        '6. Give two advantages and two disadvantages of a traditional economy.',
                    ],
                },
                'quiz': [
                    ('mcq', 'The basic economic problem is:',
                     ['inflation', 'scarcity', 'unemployment', 'taxation'], 1),
                    ('tf', 'Opportunity cost is the next-best alternative you give up.', True),
                    ('mcq', 'In a traditional economy, decisions are mainly based on:',
                     ['the government\'s plan', 'prices and profit', 'custom and tradition', 'the stock market'], 2),
                    ('tf', '"How much tax to pay?" is one of the three basic economic questions.', False),
                ],
                'homework': {
                    'title': 'Choices and opportunity costs',
                    'instructions': 'Think about choices in your own life.',
                    'tasks': [
                        'Describe three choices you or your family made this week and the opportunity cost of each.',
                        'Explain how your community answers ONE of the three economic questions.',
                    ],
                    'marks': 10,
                },
            },
            {
                'title': 'Market and command economies',
                'minutes': 45,
                'objectives': [
                    'I can describe the characteristics of a market economy.',
                    'I can describe the characteristics of a command economy.',
                    'I can compare their advantages and disadvantages.',
                ],
                'notes': (
                    '<p>In a <strong>market (free-market or capitalist) economy</strong>, the economic questions are answered '
                    'by <strong>demand and supply</strong> in markets, through the price mechanism.</p>'
                    '<ul><li>Resources and businesses are <strong>privately owned</strong>.</li>'
                    '<li>Producers decide what to make in order to earn a <strong>profit</strong>.</li>'
                    '<li>Consumers have freedom of choice; <em>competition</em> keeps prices down and quality up.</li>'
                    '<li>Government plays a small role (law and order, defence).</li></ul>'
                    '<p>Advantages: efficiency, innovation, wide choice. Disadvantages: big gaps between rich and poor, '
                    'some needed goods (e.g. street lights) are not provided, monopolies and pollution can occur.</p>'
                    '<p>In a <strong>command (centrally planned or socialist) economy</strong>, the <strong>state</strong> '
                    'answers the economic questions.</p>'
                    '<ul><li>Government owns most resources and businesses.</li>'
                    '<li>Central planners decide what is produced, how and for whom, and set prices and wages.</li>'
                    '<li>The aim is to meet everyone\'s basic needs and reduce inequality.</li></ul>'
                    '<p>Advantages: basic needs and jobs for all, less inequality. Disadvantages: little choice, '
                    'shortages and queues, little reward for hard work or new ideas, inefficiency. Examples: '
                    'North Korea, Cuba and the former Soviet Union.</p>'
                ),
                'key_terms': [
                    ('Market economy', 'Economic questions answered by demand, supply and prices'),
                    ('Command economy', 'Economic questions answered by government planning'),
                    ('Private ownership', 'Resources owned by individuals and businesses'),
                    ('Price mechanism', 'The way prices adjust to balance demand and supply'),
                    ('Competition', 'Rivalry between producers for customers'),
                ],
                'example': {
                    'title': 'Class activity: two islands',
                    'html': (
                        '<p>Split the class into two "islands", each with the same resources (cards for land, workers, tools).</p>'
                        '<ol><li><strong>Island Market:</strong> each group decides what to produce and sets its own prices to '
                        'make a profit.</li>'
                        '<li><strong>Island Command:</strong> one "planner" decides what every group produces and who receives it.</li>'
                        '<li>Compare: which island had more variety? Which shared more equally? Who was happier and why?</li></ol>'
                    ),
                },
                'video': {'id': '1DwTP0uKBrI', 'title': 'Gr9 EMS: Eco. & Entr. | Term 1 | Lesson 2 | Economic systems - Market economy',
                          'channel': 'Thuma Mina Teaching', 'minutes': 10},
                'worksheet': {
                    'instructions': 'Answer the questions; use a table for question 5.',
                    'exercises': [
                        '1. Who answers the economic questions in a market economy?',
                        '2. What is the role of profit in a market economy?',
                        '3. Who owns most resources in a command economy?',
                        '4. Why can a command economy have shortages and queues?',
                        '5. Draw a table comparing market and command economies: ownership, decisions, prices, choice, equality.',
                        '6. Give one example of a country with a mainly command economy.',
                    ],
                },
                'quiz': [
                    ('mcq', 'In a market economy, prices are mainly set by:',
                     ['the government', 'demand and supply', 'tradition', 'the church'], 1),
                    ('mcq', 'Which is a feature of a command economy?',
                     ['Private ownership of most businesses', 'Wide consumer choice',
                      'Central planning by the state', 'Competition between firms'], 2),
                    ('tf', 'A disadvantage of a market economy is a large gap between rich and poor.', True),
                    ('tf', 'In a command economy, consumers decide what is produced.', False),
                ],
                'homework': {
                    'title': 'Debate notes',
                    'instructions': 'Prepare for a short class debate.',
                    'tasks': [
                        'Write three arguments FOR a market economy.',
                        'Write three arguments FOR a command economy.',
                        'State which system you prefer and why (about 80 words).',
                    ],
                    'marks': 15,
                },
            },
            {
                'title': 'Mixed economies and South Africa',
                'minutes': 45,
                'objectives': [
                    'I can describe the features of a mixed economy.',
                    'I can explain why South Africa is a mixed economy.',
                    'I can give examples of public and private sector activity in South Africa.',
                ],
                'notes': (
                    '<p>No country today is a pure market or pure command economy. Most are <strong>mixed economies</strong>, '
                    'combining features of both.</p>'
                    '<ul><li>The <strong>private sector</strong> (individuals and businesses) owns and runs most businesses '
                    'and makes decisions based on profit and demand and supply.</li>'
                    '<li>The <strong>public sector</strong> (government) provides public goods and services, owns some '
                    'enterprises, and makes rules to protect consumers, workers and the environment.</li>'
                    '<li>Government <em>redistributes</em> income through taxes and spending (grants, free schools, clinics).</li></ul>'
                    '<p><strong>South Africa is a mixed economy:</strong></p>'
                    '<ul><li>Private companies: banks, supermarkets, mines, cellphone networks, factories.</li>'
                    '<li>State-owned enterprises (SOEs): Eskom (electricity), Transnet (rail and ports), '
                    'SAA, the SABC.</li>'
                    '<li>Government provides education, health care, social grants, police and roads, and regulates prices '
                    'of some items (e.g. fuel) and working conditions (e.g. minimum wage, labour laws).</li></ul>'
                    '<p>Advantages: choice and efficiency of markets plus protection of the poor. Challenges: high taxes, '
                    'possible inefficiency in state enterprises, and finding the right balance between the two sectors.</p>'
                ),
                'key_terms': [
                    ('Mixed economy', 'An economy with both private and public sector decision-making'),
                    ('Private sector', 'Businesses owned by individuals and companies'),
                    ('Public sector', 'Government and the services and enterprises it owns'),
                    ('State-owned enterprise', 'A business owned by the government, e.g. Eskom'),
                    ('Redistribution', 'Moving income from richer to poorer through taxes and spending'),
                ],
                'example': {
                    'title': 'Guided activity: public or private?',
                    'html': (
                        '<p>Classify each as public sector or private sector:</p>'
                        '<p><em>Eskom, a spaza shop, a public hospital, a private cellphone network, Transnet, a local '
                        'taxi owner, the South African Police Service, a supermarket chain.</em></p>'
                        '<p><strong>Public:</strong> Eskom, public hospital, Transnet, SAPS. '
                        '<strong>Private:</strong> spaza shop, cellphone network, taxi owner, supermarket chain.</p>'
                        '<p>Conclusion: both sectors are active, so South Africa has a mixed economy.</p>'
                    ),
                },
                'video': {'id': 'PScwTIYPuSI', 'title': 'Gr9 EMS: Eco. & Entr. | Term 1 | Lesson 3 | Economic systems - Mixed economy',
                          'channel': 'Thuma Mina Teaching', 'minutes': 10},
                'worksheet': {
                    'instructions': 'Answer in full sentences.',
                    'exercises': [
                        '1. Define a mixed economy.',
                        '2. What is the difference between the public sector and the private sector?',
                        '3. Name three state-owned enterprises in South Africa.',
                        '4. Give three ways the South African government is involved in the economy.',
                        '5. Why do most countries choose a mixed economy?',
                        '6. Name one challenge of a mixed economy.',
                    ],
                },
                'quiz': [
                    ('mcq', 'South Africa has a:',
                     ['pure command economy', 'traditional economy', 'mixed economy', 'pure market economy'], 2),
                    ('mcq', 'Which is a state-owned enterprise?', ['A spaza shop', 'Eskom', 'A private bank', 'A taxi'], 1),
                    ('tf', 'In a mixed economy, both the private and the public sectors make economic decisions.', True),
                    ('tf', 'Social grants are an example of a pure market economy at work.', False),
                ],
                'homework': {
                    'title': 'Economic systems mind map',
                    'instructions': 'Summarise the week\'s work.',
                    'tasks': [
                        'Draw a mind map of the four economic systems with two features and one example of each.',
                        'Find a news article about the South African economy and say whether it is about the public or private sector.',
                    ],
                    'marks': 15,
                },
            },
        ],
    },

    # ------------------------------------------------------------ CREATIVE-ARTS 7
    (7, 'CREATIVE-ARTS'): {
        'topic': 'Visual Arts: the elements of art',
        'caps': 'Creative Arts Gr 7, Term 1, Visual Arts - Create in 2D: visual literacy and the '
                'elements of art (line, shape, form, tone, texture, colour, space)',
        'summary': 'Learners are introduced to the seven elements of art and explore line, shape '
                   'and texture through drawing exercises.',
        'days': [
            {
                'title': 'Introducing the seven elements of art',
                'minutes': 45,
                'objectives': [
                    'I can name the seven elements of art.',
                    'I can identify the elements in an artwork.',
                    'I can use art vocabulary to describe what I see.',
                ],
                'notes': (
                    '<p>Artists use basic building blocks to make every artwork. These are the <strong>elements of art</strong>:</p>'
                    '<ol><li><strong>Line</strong> - a mark made by a moving point (thick, thin, straight, curved, zigzag).</li>'
                    '<li><strong>Shape</strong> - a flat, closed area with two dimensions (height and width): circles, squares '
                    'or free-form shapes.</li>'
                    '<li><strong>Form</strong> - a three-dimensional shape with height, width and depth (a sphere, cube or sculpture).</li>'
                    '<li><strong>Tone (value)</strong> - how light or dark something is.</li>'
                    '<li><strong>Texture</strong> - how something feels, or looks like it would feel (rough, smooth, furry).</li>'
                    '<li><strong>Colour</strong> - hues such as red, blue and yellow, and their mixtures.</li>'
                    '<li><strong>Space</strong> - the area around, between and within objects; it can create depth.</li></ol>'
                    '<p>Learning these elements gives you a <strong>visual language</strong>. When we look at art, we can '
                    'talk about it clearly: "The artist uses thick, curved lines and dark tones to make the picture feel heavy."</p>'
                    '<p>South African artists use these elements in many ways, for example the bold lines and bright colours '
                    'of Ndebele wall painting.</p>'
                ),
                'key_terms': [
                    ('Elements of art', 'The basic visual building blocks of an artwork'),
                    ('Shape', 'A flat (2D) enclosed area'),
                    ('Form', 'A 3D object with height, width and depth'),
                    ('Tone', 'Lightness or darkness'),
                ],
                'example': {
                    'title': 'Class activity: element detectives',
                    'html': (
                        '<p>Show a picture of an Ndebele painted house and a still-life painting.</p>'
                        '<ol><li>In pairs, learners find and list as many elements as they can in each picture.</li>'
                        '<li>For each element, write one describing word (e.g. line - bold, straight).</li>'
                        '<li>Share: which element stands out most in each artwork?</li></ol>'
                    ),
                },
                'video': {'id': 'iSbm21bhXVk', 'title': 'The Elements of Art . . . Defined!',
                          'channel': 'Design Dojo', 'minutes': 5},
                'worksheet': {
                    'instructions': 'Answer the questions. Draw small sketches where asked.',
                    'exercises': [
                        '1. List the seven elements of art.',
                        '2. What is the difference between shape and form? Sketch one example of each.',
                        '3. Define tone in your own words.',
                        '4. Name three textures you can feel in the classroom.',
                        '5. Divide a block into four. Draw a different type of line in each part.',
                        '6. Choose an object in the room and describe it using three elements of art.',
                    ],
                },
                'quiz': [
                    ('mcq', 'Which element describes how light or dark something is?',
                     ['Texture', 'Line', 'Tone', 'Space'], 2),
                    ('tf', 'A shape is flat (2D), while a form is three-dimensional.', True),
                    ('mcq', 'How many elements of art are there?', ['Five', 'Seven', 'Nine', 'Three'], 1),
                    ('tf', 'Texture can only be felt, never seen.', False),
                ],
                'homework': {
                    'title': 'Elements at home',
                    'instructions': 'Find examples of the elements of art around your home.',
                    'tasks': [
                        'Find (and sketch) one example of each of the seven elements of art at home.',
                        'Label each sketch with the element and a describing word.',
                    ],
                    'marks': 14,
                },
            },
            {
                'title': 'Line: the starting point of drawing',
                'minutes': 45,
                'objectives': [
                    'I can draw different types of line.',
                    'I can explain how lines show movement and feeling.',
                    'I can use line to create a pattern and an outline drawing.',
                ],
                'notes': (
                    '<p>A <strong>line</strong> is the path of a moving point. It is the most basic element of art and is '
                    'usually the first thing we use when we draw.</p>'
                    '<p><strong>Types of line:</strong> straight, curved, zigzag, wavy, spiral, broken (dotted or dashed), '
                    'thick, thin, horizontal, vertical and diagonal.</p>'
                    '<p><strong>What lines can do:</strong></p>'
                    '<ul><li><strong>Show feeling:</strong> horizontal lines feel calm; vertical lines feel strong and tall; '
                    'diagonal and zigzag lines feel active or tense; curved lines feel soft and flowing.</li>'
                    '<li><strong>Make outlines</strong> (contour lines) that show the edge of a shape.</li>'
                    '<li><strong>Create texture and tone</strong> with hatching (parallel lines) and cross-hatching '
                    '(lines that cross).</li>'
                    '<li><strong>Lead the eye</strong> around a picture.</li></ul>'
                    '<p><strong>Implied lines</strong> are not drawn but our eyes join them, such as the direction a person '
                    'is looking. Practise using a pencil with control: vary your pressure to make light and dark lines.</p>'
                ),
                'key_terms': [
                    ('Line', 'The path of a moving point'),
                    ('Contour line', 'A line that shows the outline or edge of an object'),
                    ('Hatching', 'Parallel lines used to show tone or texture'),
                    ('Cross-hatching', 'Crossing lines used to create darker tones'),
                ],
                'example': {
                    'title': 'Drawing activity: line sampler',
                    'html': (
                        '<ol><li>Fold an A4 page into eight blocks.</li>'
                        '<li>In each block fill the space with one type of line: straight, curved, zigzag, spiral, broken, '
                        'thick and thin, hatching and cross-hatching.</li>'
                        '<li>Under each block, write a feeling word the lines suggest (e.g. zigzag - excited).</li>'
                        '<li>Then draw the outline of your hand and fill it with lines that show your mood today.</li></ol>'
                    ),
                },
                'video': {'id': 'BDePyEFT1gQ', 'title': 'Elements of Art: Line | KQED Arts',
                          'channel': 'Art School', 'minutes': 4},
                'worksheet': {
                    'instructions': 'Use a pencil. Answer and draw.',
                    'exercises': [
                        '1. Define line in art.',
                        '2. Draw five different types of line and name each one.',
                        '3. What feeling does a horizontal line give? A diagonal line?',
                        '4. What is the difference between hatching and cross-hatching? Draw both.',
                        '5. What is an implied line?',
                        '6. Draw a simple landscape using only lines (no shading).',
                    ],
                },
                'quiz': [
                    ('mcq', 'Which type of line usually feels calm and restful?',
                     ['Zigzag', 'Diagonal', 'Horizontal', 'Spiral'], 2),
                    ('mcq', 'Lines that cross each other to create darker tone are called:',
                     ['cross-hatching', 'contour lines', 'stippling', 'implied lines'], 0),
                    ('tf', 'A contour line shows the outline or edge of an object.', True),
                    ('tf', 'Lines cannot show feelings or movement.', False),
                ],
                'homework': {
                    'title': 'Line drawing of an object',
                    'instructions': 'Choose a household object (a shoe, a cup, a plant).',
                    'tasks': [
                        'Draw its outline using a contour line.',
                        'Add details and texture using only different types of line (hatching, curved, broken).',
                    ],
                    'marks': 10,
                },
            },
            {
                'title': 'Shape and texture',
                'minutes': 45,
                'objectives': [
                    'I can tell geometric shapes from organic shapes.',
                    'I can explain actual and implied (visual) texture.',
                    'I can make a texture rubbing collage.',
                ],
                'notes': (
                    '<p>A <strong>shape</strong> is formed when a line meets itself to enclose an area. Shapes are flat (2D).</p>'
                    '<ul><li><strong>Geometric shapes</strong> are regular and mathematical: circles, squares, triangles, '
                    'rectangles. They often appear in human-made objects and in Ndebele and Sotho (litema) designs.</li>'
                    '<li><strong>Organic (free-form) shapes</strong> are irregular and flowing, like leaves, clouds and animals.</li>'
                    '<li><strong>Positive shapes</strong> are the objects themselves; <strong>negative shapes</strong> are the '
                    'spaces around them.</li></ul>'
                    '<p><strong>Texture</strong> is the surface quality of something.</p>'
                    '<ul><li><strong>Actual (real) texture</strong> can be felt with your fingers, e.g. tree bark, sandpaper, '
                    'woven baskets.</li>'
                    '<li><strong>Implied (visual) texture</strong> is drawn or painted to look like a texture, but is smooth '
                    'to touch, e.g. a drawing of fur.</li></ul>'
                    '<p>Artists create implied texture with marks such as dots (stippling), short lines, hatching and '
                    'scribbles. A <strong>rubbing</strong> (frottage) is made by placing paper over a textured surface and '
                    'rubbing with the side of a crayon or pencil.</p>'
                ),
                'key_terms': [
                    ('Geometric shape', 'A regular, mathematical shape'),
                    ('Organic shape', 'An irregular, natural shape'),
                    ('Actual texture', 'Texture you can really feel'),
                    ('Implied texture', 'Texture that is drawn to look real'),
                    ('Rubbing (frottage)', 'Copying a texture by rubbing paper over a surface'),
                ],
                'example': {
                    'title': 'Art activity: texture collage animal',
                    'html': (
                        '<ol><li>Make at least six rubbings of different surfaces (leaves, brick, mesh, coins, bark, fabric).</li>'
                        '<li>Draw a simple animal using organic shapes, and a background using geometric shapes.</li>'
                        '<li>Cut the rubbings into shapes and glue them onto the animal to give it texture.</li>'
                        '<li>Reflect: which rubbing worked best and why?</li></ol>'
                    ),
                },
                'video': {'id': 'YoOb3JSDAUo', 'title': 'Elements of Art: Texture | KQED Arts',
                          'channel': 'Art School', 'minutes': 4},
                'worksheet': {
                    'instructions': 'Answer the questions and sketch where asked.',
                    'exercises': [
                        '1. What is the difference between geometric and organic shapes? Draw two of each.',
                        '2. Explain positive and negative shapes.',
                        '3. What is the difference between actual and implied texture?',
                        '4. Name four surfaces with interesting actual textures.',
                        '5. Draw four small squares and fill each with a different implied texture.',
                        '6. How is a rubbing (frottage) made?',
                    ],
                },
                'quiz': [
                    ('mcq', 'A leaf is an example of a(n):',
                     ['geometric shape', 'organic shape', 'form', 'line'], 1),
                    ('tf', 'A drawing of fur that is smooth to touch shows implied texture.', True),
                    ('mcq', 'The space around an object in a picture is a:',
                     ['positive shape', 'geometric shape', 'negative shape', 'form'], 2),
                    ('tf', 'A triangle is an organic shape.', False),
                ],
                'homework': {
                    'title': 'Texture hunt',
                    'instructions': 'Collect textures at home.',
                    'tasks': [
                        'Make five rubbings of different surfaces at home and label each.',
                        'Draw one object showing implied texture with pencil marks.',
                    ],
                    'marks': 10,
                },
            },
        ],
    },

    # ------------------------------------------------------------ CREATIVE-ARTS 8
    (8, 'CREATIVE-ARTS'): {
        'topic': 'Visual Arts: colour and tone',
        'caps': 'Creative Arts Gr 8, Term 1, Visual Arts - Create in 2D: visual literacy and elements '
                'of art with a focus on colour (colour wheel, colour schemes) and tone',
        'summary': 'Learners build a colour wheel, explore colour schemes and the mood of warm and '
                   'cool colours, and create tonal scales.',
        'days': [
            {
                'title': 'The colour wheel',
                'minutes': 45,
                'objectives': [
                    'I can name the primary, secondary and tertiary colours.',
                    'I can mix secondary and tertiary colours.',
                    'I can construct a 12-part colour wheel.',
                ],
                'notes': (
                    '<p><strong>Colour</strong> is one of the most powerful elements of art. The <strong>colour wheel</strong> '
                    'shows how colours relate to each other.</p>'
                    '<ul><li><strong>Primary colours:</strong> red, yellow and blue. They cannot be made by mixing other paints.</li>'
                    '<li><strong>Secondary colours:</strong> made by mixing two primaries in equal amounts: '
                    'red + yellow = orange; yellow + blue = green; blue + red = violet (purple).</li>'
                    '<li><strong>Tertiary colours:</strong> made by mixing a primary with the secondary next to it, e.g. '
                    'yellow-orange, red-orange, red-violet, blue-violet, blue-green, yellow-green. The primary is named first.</li></ul>'
                    '<p>A full wheel has 12 colours: 3 primary, 3 secondary and 6 tertiary.</p>'
                    '<p><strong>Colour terms:</strong></p>'
                    '<ul><li><strong>Hue</strong> - the name of a pure colour.</li>'
                    '<li><strong>Tint</strong> - a colour plus white (lighter).</li>'
                    '<li><strong>Shade</strong> - a colour plus black (darker).</li>'
                    '<li><strong>Intensity (saturation)</strong> - how bright or dull a colour is.</li></ul>'
                    '<p>Tip: when mixing, start with the lighter colour and add small amounts of the darker one.</p>'
                ),
                'key_terms': [
                    ('Primary colours', 'Red, yellow and blue'),
                    ('Secondary colours', 'Orange, green and violet'),
                    ('Tertiary colour', 'A mix of a primary and a neighbouring secondary'),
                    ('Tint', 'A colour mixed with white'),
                    ('Shade', 'A colour mixed with black'),
                ],
                'example': {
                    'title': 'Art activity: paint a colour wheel',
                    'html': (
                        '<ol><li>Draw a circle (about 15 cm) and divide it into 12 equal segments (like a clock).</li>'
                        '<li>Paint the primaries at 12, 4 and 8 o\'clock.</li>'
                        '<li>Mix and paint the secondaries halfway between them (2, 6 and 10 o\'clock).</li>'
                        '<li>Mix and paint the six tertiaries in the remaining spaces.</li>'
                        '<li>Label every segment.</li></ol>'
                    ),
                },
                'video': {'id': '4L5aq4z9MQo',
                          'title': 'Primary, Secondary & Tertiary Colors | Quick Guide | Know Your Colors 🎨 | Color Wheel Basics',
                          'channel': 'SJ Creates', 'minutes': 3},
                'worksheet': {
                    'instructions': 'Answer the questions. Use colour pencils where possible.',
                    'exercises': [
                        '1. Name the three primary colours.',
                        '2. Which two primaries make green? Orange? Violet?',
                        '3. How is a tertiary colour made? Name all six.',
                        '4. What is the difference between a tint and a shade?',
                        '5. Draw a 12-part colour wheel and colour it in.',
                        '6. Why should you add a dark colour to a light colour when mixing, not the other way around?',
                    ],
                },
                'quiz': [
                    ('mcq', 'Which is a secondary colour?', ['Red', 'Blue', 'Green', 'Yellow'], 2),
                    ('mcq', 'A colour mixed with white is called a:', ['shade', 'tint', 'hue', 'tone'], 1),
                    ('tf', 'Blue-green is a tertiary colour.', True),
                    ('tf', 'Mixing red and blue makes orange.', False),
                ],
                'homework': {
                    'title': 'Colour mixing chart',
                    'instructions': 'Use paint, crayons or colour pencils.',
                    'tasks': [
                        'Make a chart showing how each secondary colour is mixed from two primaries.',
                        'Choose one colour and make a strip with two tints and two shades of it.',
                    ],
                    'marks': 10,
                },
            },
            {
                'title': 'Colour schemes and mood',
                'minutes': 45,
                'objectives': [
                    'I can identify warm and cool colours and the moods they create.',
                    'I can describe complementary, analogous and monochromatic colour schemes.',
                    'I can choose a colour scheme to express a feeling.',
                ],
                'notes': (
                    '<p><strong>Warm colours</strong> (reds, oranges, yellows) remind us of fire and the sun. They feel '
                    'energetic, happy or angry, and seem to come forward in a picture. <strong>Cool colours</strong> '
                    '(blues, greens, violets) remind us of water, sky and plants. They feel calm, peaceful or sad, and '
                    'seem to move back into the distance.</p>'
                    '<p>A <strong>colour scheme</strong> is a planned group of colours used together:</p>'
                    '<ul><li><strong>Complementary:</strong> colours opposite each other on the wheel (red and green, blue and '
                    'orange, yellow and violet). Placed side by side they create strong contrast; mixed together they make '
                    'a dull brown or grey.</li>'
                    '<li><strong>Analogous:</strong> three or four colours next to each other on the wheel (yellow, '
                    'yellow-green, green). They create harmony.</li>'
                    '<li><strong>Monochromatic:</strong> one hue with its tints and shades, e.g. light blue, blue, navy.</li></ul>'
                    '<p>Artists choose colour to express <strong>mood</strong>. Colours can also have cultural meanings: '
                    'for example white is worn for mourning in some cultures and for weddings in others.</p>'
                ),
                'key_terms': [
                    ('Warm colours', 'Reds, oranges and yellows'),
                    ('Cool colours', 'Blues, greens and violets'),
                    ('Complementary colours', 'Colours opposite each other on the colour wheel'),
                    ('Analogous colours', 'Colours next to each other on the colour wheel'),
                    ('Monochromatic', 'Using tints and shades of one colour'),
                ],
                'example': {
                    'title': 'Art activity: same picture, two moods',
                    'html': (
                        '<ol><li>Draw the same simple landscape (hills, a tree, a sun) twice.</li>'
                        '<li>Colour the first using only warm colours and the second using only cool colours.</li>'
                        '<li>Display them side by side. Which feels like a hot afternoon? Which feels like a cold evening?</li>'
                        '<li>Write two sentences explaining how the colours change the mood.</li></ol>'
                    ),
                },
                'video': {'id': 'DWfvn_OKQd0',
                          'title': 'Warm and Cool Colors - What makes a color warm or cool? | Color Theory | Art School | Riekreate',
                          'channel': 'Riekreate', 'minutes': 6},
                'worksheet': {
                    'instructions': 'Answer the questions.',
                    'exercises': [
                        '1. List three warm and three cool colours.',
                        '2. What moods do warm colours often create? And cool colours?',
                        '3. Name the complementary colour of red, of blue and of yellow.',
                        '4. Give an example of an analogous colour scheme.',
                        '5. What is a monochromatic colour scheme?',
                        '6. Which colour scheme would you use for a poster about a music festival? Explain.',
                    ],
                },
                'quiz': [
                    ('mcq', 'The complementary colour of blue is:', ['green', 'violet', 'orange', 'red'], 2),
                    ('tf', 'Warm colours seem to come forward in a picture.', True),
                    ('mcq', 'Yellow, yellow-green and green together form a(n):',
                     ['analogous scheme', 'complementary scheme', 'monochromatic scheme', 'primary scheme'], 0),
                    ('tf', 'A monochromatic scheme uses many different hues.', False),
                ],
                'homework': {
                    'title': 'Colour in advertising',
                    'instructions': 'Look at adverts, logos or packaging at home or in a shop.',
                    'tasks': [
                        'Find two logos or packages that use warm colours and two that use cool colours.',
                        'For each, explain the feeling the company wants to create.',
                    ],
                    'marks': 10,
                },
            },
            {
                'title': 'Tone: creating light and shadow',
                'minutes': 45,
                'objectives': [
                    'I can draw a tonal scale from light to dark.',
                    'I can use shading techniques to make shapes look 3D.',
                    'I can identify the highlight, mid-tone, shadow and cast shadow.',
                ],
                'notes': (
                    '<p><strong>Tone (value)</strong> is the lightness or darkness of a colour or a pencil mark. Artists use '
                    'tone to make flat shapes look like solid, three-dimensional <strong>forms</strong>.</p>'
                    '<p>A <strong>tonal scale</strong> shows a gradual change from white to black in steps (usually 5 to 9).</p>'
                    '<p><strong>Light on a form:</strong></p>'
                    '<ul><li><strong>Highlight</strong> - the brightest spot, where light hits directly.</li>'
                    '<li><strong>Mid-tone</strong> - the in-between areas.</li>'
                    '<li><strong>Core shadow</strong> - the darkest part of the object, facing away from the light.</li>'
                    '<li><strong>Cast shadow</strong> - the shadow the object throws onto the surface beside it.</li></ul>'
                    '<p><strong>Shading techniques:</strong> blending (smooth graduated tone), hatching, cross-hatching, '
                    'stippling (dots) and scribbling. Use a soft pencil (2B to 6B) for dark tones and a hard pencil '
                    '(HB) for light tones. Control your pressure.</p>'
                    '<p>High <strong>contrast</strong> (very light next to very dark) creates drama; low contrast feels soft and quiet.</p>'
                ),
                'key_terms': [
                    ('Tone (value)', 'Lightness or darkness'),
                    ('Tonal scale', 'Steps of tone from light to dark'),
                    ('Highlight', 'The lightest area where light hits'),
                    ('Cast shadow', 'The shadow an object throws onto a surface'),
                    ('Stippling', 'Shading with dots'),
                ],
                'example': {
                    'title': 'Drawing activity: shading a sphere',
                    'html': (
                        '<ol><li>Draw a 7-step tonal scale with a 4B pencil, from white to the darkest dark.</li>'
                        '<li>Draw a circle. Decide where the light comes from (e.g. top left).</li>'
                        '<li>Leave a small highlight near the top left. Shade gradually darker towards the bottom right.</li>'
                        '<li>Add a cast shadow on the "table" on the side away from the light.</li>'
                        '<li>Compare with a flat circle: the circle now looks like a ball.</li></ol>'
                    ),
                },
                'video': {'id': '-Z7_NulZ2HU', 'title': 'Making A Value Scale',
                          'channel': 'Abington Art Studio', 'minutes': 5},
                'worksheet': {
                    'instructions': 'Use a soft pencil.',
                    'exercises': [
                        '1. Define tone.',
                        '2. Draw a tonal scale of seven blocks from white to black.',
                        '3. Draw a cube and shade it so that each face has a different tone.',
                        '4. Label the highlight, mid-tone, core shadow and cast shadow on a shaded sphere.',
                        '5. Draw a small square for each: blending, hatching, cross-hatching, stippling.',
                        '6. What effect does high contrast have in a drawing?',
                    ],
                },
                'quiz': [
                    ('mcq', 'The brightest area on a shaded object is the:',
                     ['cast shadow', 'core shadow', 'highlight', 'mid-tone'], 2),
                    ('tf', 'Stippling is shading with dots.', True),
                    ('mcq', 'Which pencil is best for very dark tones?', ['2H', 'HB', '6B', '4H'], 2),
                    ('tf', 'An HB pencil makes darker tones than a 6B pencil.', False),
                ],
                'homework': {
                    'title': 'Tonal still life',
                    'instructions': 'Set up two or three simple objects (a cup, an apple, a box) near a window or lamp.',
                    'tasks': [
                        'Draw the objects and shade them using at least five tones.',
                        'Show the highlights and cast shadows clearly.',
                    ],
                    'marks': 15,
                },
            },
        ],
    },

    # ------------------------------------------------------------ CREATIVE-ARTS 9
    (9, 'CREATIVE-ARTS'): {
        'topic': 'Visual Arts: design principles and drawing from observation',
        'caps': 'Creative Arts Gr 9, Term 1, Visual Arts - Create in 2D: visual literacy, design '
                'principles (balance, contrast, emphasis, rhythm, unity, proportion), observational '
                'drawing and perspective',
        'summary': 'Learners use the principles of design to analyse and plan artworks, practise '
                   'contour drawing from observation and draw in one-point perspective.',
        'days': [
            {
                'title': 'The principles of design',
                'minutes': 50,
                'objectives': [
                    'I can explain the main principles of design.',
                    'I can analyse how an artwork uses the principles.',
                    'I can distinguish symmetrical from asymmetrical balance.',
                ],
                'notes': (
                    '<p>The <strong>elements</strong> of art are the ingredients; the <strong>principles of design</strong> '
                    'are the ways artists <em>arrange</em> those ingredients in a <strong>composition</strong>.</p>'
                    '<ul><li><strong>Balance</strong> - the even spread of visual weight. <em>Symmetrical</em> balance is '
                    'the same on both sides (formal); <em>asymmetrical</em> balance uses different objects that still '
                    'feel equal (informal); <em>radial</em> balance spreads out from a centre.</li>'
                    '<li><strong>Contrast</strong> - strong differences (light/dark, rough/smooth, large/small) that add interest.</li>'
                    '<li><strong>Emphasis (focal point)</strong> - the area that draws the eye first.</li>'
                    '<li><strong>Rhythm and pattern</strong> - repetition of elements that creates movement.</li>'
                    '<li><strong>Proportion and scale</strong> - the size of parts in relation to each other.</li>'
                    '<li><strong>Unity and variety</strong> - the sense that everything belongs together, with enough '
                    'difference to stay interesting.</li></ul>'
                    '<p>When you discuss an artwork, use a simple method: <em>describe</em> what you see, '
                    '<em>analyse</em> the elements and principles, <em>interpret</em> the meaning and '
                    '<em>judge</em> how successful it is.</p>'
                ),
                'key_terms': [
                    ('Composition', 'The arrangement of elements in an artwork'),
                    ('Balance', 'Even distribution of visual weight'),
                    ('Emphasis', 'The focal point that attracts attention first'),
                    ('Rhythm', 'Repetition that creates a sense of movement'),
                    ('Unity', 'The feeling that all parts belong together'),
                ],
                'example': {
                    'title': 'Class activity: analyse an artwork',
                    'html': (
                        '<p>Show a reproduction of a well-known South African artwork (e.g. a work by Gerard Sekoto or '
                        'Esther Mahlangu).</p>'
                        '<ol><li><strong>Describe:</strong> list everything you see.</li>'
                        '<li><strong>Analyse:</strong> where is the focal point? Is the balance symmetrical or asymmetrical? '
                        'Where is there contrast or rhythm?</li>'
                        '<li><strong>Interpret:</strong> what mood or message does it give?</li>'
                        '<li><strong>Judge:</strong> do the principles work well together? Why?</li></ol>'
                    ),
                },
                'video': {'id': 'otmlOU4_d8U', 'title': '5 Basic Principles of Design',
                          'channel': 'Worlds Away', 'minutes': 5},
                'worksheet': {
                    'instructions': 'Answer the questions; sketch thumbnails where asked.',
                    'exercises': [
                        '1. What is the difference between elements of art and principles of design?',
                        '2. Sketch a thumbnail composition with symmetrical balance and one with asymmetrical balance.',
                        '3. Name three ways an artist can create emphasis.',
                        '4. Explain rhythm and give an example from African craft or design.',
                        '5. Why do artworks need both unity and variety?',
                        '6. List the four steps for discussing an artwork.',
                    ],
                },
                'quiz': [
                    ('mcq', 'The part of an artwork that attracts the eye first is the:',
                     ['rhythm', 'focal point (emphasis)', 'background', 'proportion'], 1),
                    ('tf', 'Asymmetrical balance uses different objects that still feel equal in visual weight.', True),
                    ('mcq', 'Repeating shapes to create a sense of movement is called:',
                     ['rhythm', 'contrast', 'balance', 'scale'], 0),
                    ('tf', 'Principles of design are the basic ingredients such as line and colour.', False),
                ],
                'homework': {
                    'title': 'Principles in everyday design',
                    'instructions': 'Look at a magazine cover, a poster or a website.',
                    'tasks': [
                        'Sketch the layout and label the focal point, the type of balance and one example of contrast.',
                        'Write a short paragraph judging how well the design works.',
                    ],
                    'marks': 15,
                },
            },
            {
                'title': 'Drawing from observation: contour drawing',
                'minutes': 50,
                'objectives': [
                    'I can explain the difference between blind contour, modified contour and cross-contour drawing.',
                    'I can draw an object accurately by looking carefully.',
                    'I can use line weight to show depth.',
                ],
                'notes': (
                    '<p><strong>Observational drawing</strong> means drawing what you actually see, not what you think '
                    'something looks like. It trains your eye and hand to work together.</p>'
                    '<p>A <strong>contour drawing</strong> uses lines to record the edges of an object - both the outer '
                    'edge and important inner edges (folds, creases, overlaps).</p>'
                    '<ul><li><strong>Blind contour:</strong> you look only at the object, never at your paper, and move your '
                    'pencil slowly as your eyes trace the edges. The result looks strange but builds close looking.</li>'
                    '<li><strong>Modified contour:</strong> you look mainly at the object but glance at the paper to check '
                    'positions.</li>'
                    '<li><strong>Cross-contour:</strong> lines that wrap around the form, like lines of latitude on a globe, '
                    'to show its volume.</li></ul>'
                    '<p><strong>Line weight</strong> (thick or thin, dark or light lines) shows depth: use darker, thicker lines '
                    'for edges that are closer or in shadow, and lighter, thinner lines for parts further away or in light.</p>'
                    '<p>Tips: measure proportions by holding your pencil at arm\'s length; draw slowly; do not erase too much.</p>'
                ),
                'key_terms': [
                    ('Observational drawing', 'Drawing from real objects by looking carefully'),
                    ('Blind contour', 'Drawing edges without looking at the paper'),
                    ('Cross-contour', 'Lines that wrap around a form to show volume'),
                    ('Line weight', 'The thickness or darkness of a line'),
                ],
                'example': {
                    'title': 'Drawing activity: three ways to see a shoe',
                    'html': (
                        '<ol><li><strong>Blind contour (3 min):</strong> draw your shoe without looking at the paper.</li>'
                        '<li><strong>Modified contour (10 min):</strong> draw it again, glancing at the paper now and then. '
                        'Include laces and stitching.</li>'
                        '<li><strong>Line weight (5 min):</strong> go over the drawing, making the edges nearest to you and in '
                        'shadow darker and thicker.</li>'
                        '<li>Compare the three drawings with a partner.</li></ol>'
                    ),
                },
                'video': {'id': '4qNMzOb-DY8', 'title': 'Contour Drawing: What Is It? How Do You Do It?',
                          'channel': 'The Pencil Room Online', 'minutes': 8},
                'worksheet': {
                    'instructions': 'Answer the questions and complete the drawing tasks.',
                    'exercises': [
                        '1. What is observational drawing?',
                        '2. Explain the difference between blind contour and modified contour drawing.',
                        '3. What are cross-contour lines used for?',
                        '4. How can line weight show depth?',
                        '5. Do a 2-minute blind contour drawing of your non-drawing hand.',
                        '6. Draw a cup using cross-contour lines to show its round form.',
                    ],
                },
                'quiz': [
                    ('mcq', 'In a blind contour drawing, you:',
                     ['look only at your paper', 'look only at the object', 'trace a photograph', 'use only colour'], 1),
                    ('tf', 'Darker, thicker lines can make an edge seem closer.', True),
                    ('mcq', 'Lines that wrap around a form to show its volume are:',
                     ['cross-contour lines', 'implied lines', 'horizon lines', 'grid lines'], 0),
                    ('tf', 'Observational drawing means drawing from memory and imagination only.', False),
                ],
                'homework': {
                    'title': 'Sketchbook observation',
                    'instructions': 'Draw from real objects at home.',
                    'tasks': [
                        'Make two modified contour drawings of objects with interesting edges (a kettle, a plant, a bag).',
                        'Use varied line weight in both drawings.',
                    ],
                    'marks': 10,
                },
            },
            {
                'title': 'One-point perspective',
                'minutes': 50,
                'objectives': [
                    'I can identify the horizon line, vanishing point and orthogonal lines.',
                    'I can draw boxes and a road in one-point perspective.',
                    'I can use perspective to create depth in a drawing.',
                ],
                'notes': (
                    '<p><strong>Perspective</strong> is a drawing method that creates the illusion of depth and distance on a '
                    'flat surface. Objects look smaller the further away they are, and parallel lines (like the sides of a '
                    'road) seem to meet in the distance.</p>'
                    '<p><strong>One-point perspective</strong> uses a single vanishing point:</p>'
                    '<ul><li><strong>Horizon line (eye level)</strong> - a horizontal line where the sky appears to meet the land.</li>'
                    '<li><strong>Vanishing point (VP)</strong> - a point on the horizon line where receding lines meet.</li>'
                    '<li><strong>Orthogonal lines</strong> - lines that go back into the picture and lead to the VP.</li>'
                    '<li>Horizontal lines stay horizontal; vertical lines stay vertical.</li></ul>'
                    '<p><strong>Drawing a box:</strong></p>'
                    '<ol><li>Draw a horizon line and mark a VP.</li>'
                    '<li>Draw a square (the front face) above or below the horizon.</li>'
                    '<li>Lightly connect its corners to the VP with orthogonal lines.</li>'
                    '<li>Draw a horizontal and a vertical line between the orthogonals to make the back edge.</li>'
                    '<li>Erase the extra lines and darken the box.</li></ol>'
                    '<p>Boxes above the horizon show their underside; boxes below show their top.</p>'
                ),
                'key_terms': [
                    ('Perspective', 'A method of showing depth on a flat surface'),
                    ('Horizon line', 'The viewer\'s eye level, where sky meets land'),
                    ('Vanishing point', 'The point where receding parallel lines meet'),
                    ('Orthogonal lines', 'Lines that lead to the vanishing point'),
                ],
                'example': {
                    'title': 'Guided drawing: a street in perspective',
                    'html': (
                        '<ol><li>Draw a horizon line across the middle of the page and a VP in the centre.</li>'
                        '<li>Draw two lines from the bottom corners of the page to the VP: this is the road.</li>'
                        '<li>Add lamp posts along the road: each is vertical and gets shorter as it gets closer to the VP '
                        '(use an orthogonal line from the top of the first post to the VP as a guide).</li>'
                        '<li>Add buildings as boxes on either side with their sides going to the VP.</li></ol>'
                    ),
                },
                'video': {'id': 'fL967_0vYA0', 'title': 'How to Draw a Simple Road using One-Point Perspective for Beginners',
                          'channel': 'Circle Line Art School', 'minutes': 8},
                'worksheet': {
                    'instructions': 'Use a ruler and a sharp pencil.',
                    'exercises': [
                        '1. Define perspective.',
                        '2. What is the horizon line?',
                        '3. What are orthogonal lines?',
                        '4. Draw a horizon line with one VP and three boxes: one above, one on and one below the horizon.',
                        '5. Why do objects get smaller as they move towards the vanishing point?',
                        '6. Draw a simple corridor or railway line in one-point perspective.',
                    ],
                },
                'quiz': [
                    ('mcq', 'The horizon line represents the:',
                     ['top of the page', 'viewer\'s eye level', 'vanishing point', 'ground'], 1),
                    ('mcq', 'Lines that lead back to the vanishing point are called:',
                     ['orthogonal lines', 'contour lines', 'horizon lines', 'hatching'], 0),
                    ('tf', 'In one-point perspective, vertical lines stay vertical.', True),
                    ('tf', 'A box drawn below the horizon line shows its underside.', False),
                ],
                'homework': {
                    'title': 'My street in perspective',
                    'instructions': 'Use one-point perspective.',
                    'tasks': [
                        'Draw a street, corridor or room in one-point perspective with at least four objects.',
                        'Mark the horizon line and vanishing point lightly, and add tone to show light and shadow.',
                    ],
                    'marks': 20,
                },
            },
        ],
    },

    # ------------------------------------------------------------------ LO 7
    (7, 'LO'): {
        'topic': 'Development of the self in society: Self-image',
        'caps': 'Life Orientation Gr 7, Term 1, Development of the self in society: self-image - '
                'understanding and accepting yourself; personal strengths, weaknesses, interests '
                'and abilities; strategies to enhance self-image and the self-image of others',
        'summary': 'Learners explore what self-image is, identify their own strengths, interests '
                   'and abilities, and practise ways to build a positive self-image in themselves '
                   'and others.',
        'days': [
            {
                'title': 'What is self-image?',
                'minutes': 40,
                'objectives': [
                    'I can explain what self-image means.',
                    'I can describe the difference between a positive and a negative self-image.',
                    'I can name things that influence how I see myself.',
                ],
                'notes': (
                    '<p>Your <strong>self-image</strong> is the picture you have of yourself: how you see your looks, your '
                    'abilities, your personality and your worth. It is closely linked to <strong>self-esteem</strong>, which '
                    'is how much you value and respect yourself.</p>'
                    '<p>A <strong>positive self-image</strong> means you accept yourself, know your strengths and are kind to '
                    'yourself about your weaknesses. People with a positive self-image usually try new things, cope better '
                    'with mistakes and treat others with respect.</p>'
                    '<p>A <strong>negative self-image</strong> means you focus on what you think is wrong with you. It can make '
                    'you shy, afraid to try, easily hurt by comments or likely to follow others to fit in.</p>'
                    '<p><strong>What shapes our self-image?</strong></p>'
                    '<ul><li>Family and how they speak to us.</li>'
                    '<li>Friends and peers.</li>'
                    '<li>Teachers, coaches and religious or community leaders.</li>'
                    '<li>Media and social media, which often show unrealistic, edited images.</li>'
                    '<li>Our own successes, failures and self-talk.</li></ul>'
                    '<p>Self-image is not fixed. You can change it by how you think and act.</p>'
                ),
                'key_terms': [
                    ('Self-image', 'The picture you have of yourself'),
                    ('Self-esteem', 'How much you value and respect yourself'),
                    ('Peers', 'People of your own age group'),
                ],
                'example': {
                    'title': 'Class activity: the mirror and the window',
                    'html': (
                        '<ol><li>On one side of a page draw a mirror. Inside it write five words describing how you see yourself.</li>'
                        '<li>On the other side draw a window. Write five words you think others would use to describe you.</li>'
                        '<li>Discuss in pairs (only if comfortable): are the two lists similar? Which words are positive?</li>'
                        '<li>Class discussion: where do our ideas about ourselves come from?</li></ol>'
                    ),
                },
                'video': {'id': 'wRhVP3KH9oM',
                          'title': '💡 GET TO KNOW YOURSELF BETTER: Self-awareness, Self-image, and Self-esteem for Kids 💖🧠',
                          'channel': 'Smile and Learn - English', 'minutes': 5},
                'worksheet': {
                    'instructions': 'Answer honestly in full sentences. Your answers are private.',
                    'exercises': [
                        '1. In your own words, what is self-image?',
                        '2. How is self-esteem linked to self-image?',
                        '3. Give two signs of a positive self-image.',
                        '4. Give two signs of a negative self-image.',
                        '5. Name three people or things that influence how you see yourself.',
                        '6. How can social media affect a teenager\'s self-image?',
                    ],
                },
                'quiz': [
                    ('mcq', 'Self-image is:',
                     ['how tall you are', 'the picture you have of yourself', 'what your friends wear', 'your school marks'], 1),
                    ('tf', 'Self-image can change over time.', True),
                    ('mcq', 'Which is a sign of a positive self-image?',
                     ['Refusing to try new things', 'Accepting your strengths and weaknesses',
                      'Always following the crowd', 'Being very hurt by every comment'], 1),
                    ('tf', 'Images on social media always show people exactly as they are.', False),
                ],
                'homework': {
                    'title': 'My influences',
                    'instructions': 'Reflect privately on what shapes your self-image.',
                    'tasks': [
                        'Draw yourself in the middle of a page with arrows to the people and things that influence how you see yourself.',
                        'Next to each arrow, write whether the influence is mostly positive or negative and why.',
                    ],
                    'marks': 10,
                },
            },
            {
                'title': 'My strengths, weaknesses, interests and abilities',
                'minutes': 40,
                'objectives': [
                    'I can identify my personal strengths and weaknesses.',
                    'I can describe my interests and abilities.',
                    'I can explain how knowing myself helps me grow.',
                ],
                'notes': (
                    '<p>Knowing yourself well is the foundation of a healthy self-image.</p>'
                    '<ul><li><strong>Strengths</strong> are qualities or skills you are good at, e.g. being kind, honest, '
                    'creative, a good listener, good at sport or maths.</li>'
                    '<li><strong>Weaknesses</strong> are areas where you struggle or still need to grow, e.g. losing your temper, '
                    'being disorganised, finding it hard to speak in front of others.</li>'
                    '<li><strong>Interests</strong> are things you enjoy and want to know more about, e.g. music, animals, cooking, '
                    'technology.</li>'
                    '<li><strong>Abilities</strong> are things you can do, which you can develop through practice.</li></ul>'
                    '<p>Everyone has strengths and weaknesses. Nobody is good at everything. A weakness is not a failure - '
                    'it is an area to work on. Often a strength can help with a weakness: a learner who is good at drawing can '
                    'use mind maps to study.</p>'
                    '<p>Knowing your strengths and interests helps you choose subjects, hobbies and later a career, and it '
                    'builds <strong>confidence</strong>. Accepting your weaknesses helps you ask for help and set goals to improve.</p>'
                ),
                'key_terms': [
                    ('Strength', 'A quality or skill you are good at'),
                    ('Weakness', 'An area where you still need to grow'),
                    ('Interest', 'Something you enjoy and want to learn about'),
                    ('Ability', 'Something you are able to do'),
                ],
                'example': {
                    'title': 'Class activity: strengths web',
                    'html': (
                        '<ol><li>Each learner writes their name in a circle in the middle of a page.</li>'
                        '<li>They write three strengths, two interests and one ability around it.</li>'
                        '<li>Pages are passed to two classmates, who each add one positive strength they have noticed.</li>'
                        '<li>Learners read their page. Was there a strength others saw that you did not?</li></ol>'
                        '<p>Rule: only kind, honest comments.</p>'
                    ),
                },
                'video': {'id': 'JwNI1F21eK8', 'title': 'Identifying Your Strengths',
                          'channel': 'BITE BACK', 'minutes': 3},
                'worksheet': {
                    'instructions': 'Complete the personal profile.',
                    'exercises': [
                        '1. List three personal strengths and give an example of when you showed each one.',
                        '2. List two weaknesses you would like to improve.',
                        '3. For one weakness, write one step you can take to improve it.',
                        '4. List three interests.',
                        '5. Name one ability you have developed through practice.',
                        '6. How can knowing your strengths help you choose your subjects in future?',
                    ],
                },
                'quiz': [
                    ('mcq', 'Something you enjoy and want to learn more about is a(n):',
                     ['weakness', 'interest', 'failure', 'rule'], 1),
                    ('tf', 'Everyone has both strengths and weaknesses.', True),
                    ('mcq', 'The best way to deal with a weakness is to:',
                     ['hide it', 'give up', 'work on it and ask for help', 'blame others'], 2),
                    ('tf', 'A weakness means you are a failure.', False),
                ],
                'homework': {
                    'title': 'Strengths interview',
                    'instructions': 'Ask a family member or trusted adult.',
                    'tasks': [
                        'Ask them to name three strengths they see in you, and write them down.',
                        'Write a short paragraph: did anything surprise you? How do you feel about it?',
                    ],
                    'marks': 10,
                },
            },
            {
                'title': 'Building a positive self-image in myself and others',
                'minutes': 40,
                'objectives': [
                    'I can use strategies to improve my own self-image.',
                    'I can show respect and build up others\' self-image.',
                    'I can recognise put-downs and replace them with positive actions.',
                ],
                'notes': (
                    '<p>You can strengthen your self-image with daily habits:</p>'
                    '<ul><li><strong>Positive self-talk:</strong> replace "I\'m useless" with "I\'m still learning".</li>'
                    '<li><strong>Celebrate achievements</strong>, big and small.</li>'
                    '<li><strong>Set small, realistic goals</strong> and work towards them.</li>'
                    '<li><strong>Look after your body:</strong> sleep, healthy food and exercise help you feel good.</li>'
                    '<li><strong>Choose supportive friends</strong> who respect you.</li>'
                    '<li><strong>Stop comparing</strong> yourself to edited images online.</li>'
                    '<li><strong>Talk to someone</strong> you trust when you feel low.</li></ul>'
                    '<p>We also affect how <em>others</em> see themselves. <strong>Put-downs</strong> (insults, teasing, '
                    'laughing at mistakes, leaving people out) hurt self-image. <strong>Build-ups</strong> help:</p>'
                    '<ul><li>Give honest compliments and encouragement.</li>'
                    '<li>Include others in activities.</li>'
                    '<li>Listen without judging.</li>'
                    '<li>Respect differences in culture, religion, looks and abilities.</li>'
                    '<li>Stand up against bullying.</li></ul>'
                    '<p>Respect for yourself and for others go together: when we build each other up, the whole class feels safer.</p>'
                ),
                'key_terms': [
                    ('Self-talk', 'The things you say to yourself in your mind'),
                    ('Put-down', 'A word or action that makes someone feel small'),
                    ('Build-up', 'A word or action that makes someone feel valued'),
                    ('Respect', 'Treating people and yourself as valuable'),
                ],
                'example': {
                    'title': 'Class activity: put-down to build-up',
                    'html': (
                        '<p>Read each put-down and rewrite it as a build-up:</p>'
                        '<ul><li>"You can\'t play soccer, go away." - "Come join us, we\'ll show you how."</li>'
                        '<li>"Your drawing is ugly." - "I like the colours you used. What will you add next?"</li>'
                        '<li>"I\'m so stupid, I failed." (self-talk) - "That was hard. I\'ll ask for help and try again."</li></ul>'
                        '<p>Then create a class "build-up wall" of kind sentences.</p>'
                    ),
                },
                'video': {'id': '5BuHC8wBdBU', 'title': 'Self-Esteem For Kids - 10 Ways To Build Self-Esteem & Self-Confidence',
                          'channel': 'Mental Health Center Kids', 'minutes': 5},
                'worksheet': {
                    'instructions': 'Answer the questions.',
                    'exercises': [
                        '1. Name four strategies to improve your self-image.',
                        '2. Change this negative self-talk into positive self-talk: "I will never understand maths."',
                        '3. What is a put-down? Give an example.',
                        '4. Name three ways you can build up a classmate.',
                        '5. How can comparing yourself to others online harm your self-image?',
                        '6. Write a kind message you could give to someone who is new at school.',
                    ],
                },
                'quiz': [
                    ('mcq', 'Which is an example of positive self-talk?',
                     ['"I always mess up."', '"I am still learning and I can improve."',
                      '"Nobody likes me."', '"I should not even try."'], 1),
                    ('tf', 'Including someone who is left out can build their self-image.', True),
                    ('mcq', 'Which is a put-down?',
                     ['Giving a compliment', 'Listening carefully', 'Laughing at someone\'s mistake', 'Saying thank you'], 2),
                    ('tf', 'How we treat others has no effect on their self-image.', False),
                ],
                'homework': {
                    'title': 'Kindness challenge',
                    'instructions': 'For three days, practise building yourself and others up.',
                    'tasks': [
                        'Each day, write one positive thing about yourself in a journal.',
                        'Each day, do or say one kind thing for someone else and record it.',
                        'Write a short reflection: how did it make you and the other person feel?',
                    ],
                    'marks': 15,
                },
            },
        ],
    },

    # ------------------------------------------------------------------ LO 8
    (8, 'LO'): {
        'topic': 'Development of the self in society: Self-concept formation and self-motivation',
        'caps': 'Life Orientation Gr 8, Term 1, Development of the self in society: self-concept '
                'formation and self-motivation - factors that influence self-concept (media, '
                'environment, friends and peers, family, culture, religion, community), positive '
                'self-talk, strategies and skills to extend personal potential',
        'summary': 'Learners examine how their self-concept forms and what influences it, practise '
                   'positive self-talk, and plan ways to stay motivated and extend their potential.',
        'days': [
            {
                'title': 'Self-concept and what shapes it',
                'minutes': 40,
                'objectives': [
                    'I can explain what self-concept is.',
                    'I can describe how media, peers, family, culture, religion and community influence self-concept.',
                    'I can reflect on the influences in my own life.',
                ],
                'notes': (
                    '<p>Your <strong>self-concept</strong> is everything you believe about yourself: your abilities, '
                    'personality, values, roles (learner, sibling, team member), looks and identity. It answers the '
                    'question "<em>Who am I?</em>". Self-concept develops throughout life, and especially during '
                    'adolescence, when your body, friendships and responsibilities change.</p>'
                    '<p><strong>Factors that influence self-concept:</strong></p>'
                    '<ul><li><strong>Family:</strong> praise, criticism, expectations and family values.</li>'
                    '<li><strong>Friends and peers:</strong> acceptance or rejection, peer pressure.</li>'
                    '<li><strong>Media and social media:</strong> idealised bodies, lifestyles and "likes" can make '
                    'teenagers feel they are not good enough.</li>'
                    '<li><strong>Culture and religion:</strong> traditions, beliefs and rites of passage give identity and values.</li>'
                    '<li><strong>Community and environment:</strong> role models, safety, opportunities and challenges '
                    'such as poverty or crime.</li>'
                    '<li><strong>Personal experiences:</strong> successes and failures at school and in sport.</li></ul>'
                    '<p>A <strong>positive self-concept</strong> helps you make healthy decisions, resist negative '
                    'pressure and keep trying after setbacks. You cannot choose all your influences, but you can choose '
                    'how you respond to them.</p>'
                ),
                'key_terms': [
                    ('Self-concept', 'All the beliefs you hold about yourself'),
                    ('Identity', 'The characteristics that make you who you are'),
                    ('Adolescence', 'The stage of development between childhood and adulthood'),
                    ('Role model', 'A person whose behaviour others look up to and copy'),
                ],
                'example': {
                    'title': 'Class activity: "Who am I?" identity map',
                    'html': (
                        '<ol><li>Write "I am..." in the centre of a page.</li>'
                        '<li>Around it write ten endings, e.g. "I am a daughter", "I am good at netball", "I am Christian", '
                        '"I am curious".</li>'
                        '<li>Next to each, write the influence that shaped it (family, peers, culture, media, community).</li>'
                        '<li>Discuss in groups: which influence is the strongest for teenagers today? Why?</li></ol>'
                    ),
                },
                'video': {'id': 'w8oOJVPrLG0', 'title': 'What is Self-Concept? (Easiest Explanation)',
                          'channel': 'Social Science Explainer', 'minutes': 5},
                'worksheet': {
                    'instructions': 'Answer in full sentences.',
                    'exercises': [
                        '1. Define self-concept.',
                        '2. Why does self-concept change a lot during adolescence?',
                        '3. Explain how family can influence self-concept positively and negatively.',
                        '4. How can social media affect self-concept? Give two examples.',
                        '5. How can culture or religion contribute to a positive self-concept?',
                        '6. Name one role model in your community and explain how they influence young people.',
                    ],
                },
                'quiz': [
                    ('mcq', 'Self-concept is best described as:',
                     ['your favourite subject', 'all the beliefs you hold about yourself',
                      'your physical fitness', 'what your parents want you to be'], 1),
                    ('tf', 'Culture and religion can influence your self-concept.', True),
                    ('mcq', 'Which is a possible negative influence of social media on self-concept?',
                     ['Learning new skills', 'Comparing yourself to edited images',
                      'Keeping in touch with family', 'Finding study help'], 1),
                    ('tf', 'Self-concept is fixed at birth and never changes.', False),
                ],
                'homework': {
                    'title': 'Influences journal',
                    'instructions': 'Keep a private record for two days.',
                    'tasks': [
                        'Note three moments when something (a person, a post, an event) made you feel better or worse about yourself.',
                        'For each, write which factor it was and how you responded.',
                    ],
                    'marks': 10,
                },
            },
            {
                'title': 'Positive self-talk',
                'minutes': 40,
                'objectives': [
                    'I can explain what self-talk is and how it affects feelings and actions.',
                    'I can recognise negative thinking patterns.',
                    'I can change negative self-talk into positive, realistic self-talk.',
                ],
                'notes': (
                    '<p><strong>Self-talk</strong> is the voice inside your head - the way you speak to yourself about '
                    'what happens. It affects how you <em>feel</em> and what you <em>do</em>. If you tell yourself "I\'m '
                    'going to fail", you may not study, which makes failing more likely.</p>'
                    '<p><strong>Common negative thinking traps:</strong></p>'
                    '<ul><li><strong>All-or-nothing:</strong> "If I don\'t get 100%, I\'m a failure."</li>'
                    '<li><strong>Over-generalising:</strong> "I always get things wrong."</li>'
                    '<li><strong>Mind reading:</strong> "Everyone thinks I\'m weird."</li>'
                    '<li><strong>Labelling:</strong> "I\'m stupid."</li></ul>'
                    '<p><strong>How to use positive self-talk:</strong></p>'
                    '<ol><li><strong>Notice</strong> the negative thought.</li>'
                    '<li><strong>Challenge</strong> it: Is it true? What evidence is there? What would I say to a friend?</li>'
                    '<li><strong>Replace</strong> it with a realistic, kind statement: "I didn\'t do well this time, but I can '
                    'learn from my mistakes."</li></ol>'
                    '<p>Positive self-talk is not pretending everything is perfect. It is being honest <em>and</em> encouraging, '
                    'and focusing on your <strong>individuality, uniqueness and personal achievements</strong>.</p>'
                ),
                'key_terms': [
                    ('Self-talk', 'The inner voice with which you speak to yourself'),
                    ('Thinking trap', 'An unhelpful, unrealistic pattern of thinking'),
                    ('Affirmation', 'A short positive statement about yourself'),
                    ('Uniqueness', 'Being the only one of your kind'),
                ],
                'example': {
                    'title': 'Guided activity: notice, challenge, replace',
                    'html': (
                        '<p><strong>Situation:</strong> Lerato is not chosen for the netball team.</p>'
                        '<p><strong>Notice:</strong> "I\'m useless at sport. Everyone is laughing at me."</p>'
                        '<p><strong>Challenge:</strong> Is that true? She made the team last year and the coach said she has good '
                        'passing skills. Nobody actually laughed.</p>'
                        '<p><strong>Replace:</strong> "I\'m disappointed, but I have good skills. I\'ll ask the coach what to '
                        'practise and try again next term."</p>'
                        '<p>Learners now do the same for: failing a test; a friend not replying to a message.</p>'
                    ),
                },
                'video': {'id': 'Punls8U9nIg', 'title': 'Self-Talk for Kids: Inner Critic vs Inner Coach',
                          'channel': 'Big Ideas for Little Humans', 'minutes': 4},
                'worksheet': {
                    'instructions': 'Complete the exercises.',
                    'exercises': [
                        '1. What is self-talk?',
                        '2. Explain how negative self-talk can affect your actions.',
                        '3. Name the thinking trap: "I always mess everything up."',
                        '4. Rewrite as positive self-talk: "I\'ll never make friends at this school."',
                        '5. Rewrite as positive self-talk: "I\'m terrible at speaking in front of people."',
                        '6. Write three affirmations about your own uniqueness or achievements.',
                    ],
                },
                'quiz': [
                    ('mcq', '"Everyone thinks I\'m weird" is an example of which thinking trap?',
                     ['Mind reading', 'Positive thinking', 'Goal setting', 'Affirmation'], 0),
                    ('tf', 'Positive self-talk means being honest and encouraging with yourself.', True),
                    ('mcq', 'The three steps to change self-talk are:',
                     ['ignore, hide, forget', 'notice, challenge, replace', 'blame, complain, quit', 'copy, paste, share'], 1),
                    ('tf', 'Self-talk has no effect on how we feel.', False),
                ],
                'homework': {
                    'title': 'Inner coach cards',
                    'instructions': 'Make cards you can keep in your bag or on your mirror.',
                    'tasks': [
                        'Write five realistic, positive statements on small cards.',
                        'Write down one situation this week where you used positive self-talk and what happened.',
                    ],
                    'marks': 10,
                },
            },
            {
                'title': 'Self-motivation and extending my potential',
                'minutes': 40,
                'objectives': [
                    'I can explain the difference between intrinsic and extrinsic motivation.',
                    'I can describe a growth mindset.',
                    'I can plan strategies to reach my potential.',
                ],
                'notes': (
                    '<p><strong>Self-motivation</strong> is the inner drive to start and keep going with a task, even when it is '
                    'difficult and nobody is pushing you.</p>'
                    '<ul><li><strong>Intrinsic motivation</strong> comes from inside: you do something because you enjoy it or '
                    'it matters to you.</li>'
                    '<li><strong>Extrinsic motivation</strong> comes from outside: rewards, marks, praise or avoiding punishment.</li></ul>'
                    '<p>Intrinsic motivation usually lasts longer.</p>'
                    '<p>A <strong>growth mindset</strong> is the belief that your abilities can develop through effort, good '
                    'strategies and help from others. A <strong>fixed mindset</strong> believes abilities cannot change ("I\'m just '
                    'not a maths person"). People with a growth mindset see mistakes as part of learning.</p>'
                    '<p><strong>Strategies to extend your potential:</strong></p>'
                    '<ul><li>Set clear, achievable goals and break them into small steps.</li>'
                    '<li>Make a timetable and stick to routines.</li>'
                    '<li>Track your progress and reward yourself.</li>'
                    '<li>Find a role model or mentor.</li>'
                    '<li>Join clubs, sports or cultural activities to discover new talents.</li>'
                    '<li>Use positive self-talk and ask for help when you are stuck.</li>'
                    '<li>Look after your health: sleep, food and exercise affect energy and focus.</li></ul>'
                ),
                'key_terms': [
                    ('Self-motivation', 'The inner drive to start and keep going'),
                    ('Intrinsic motivation', 'Motivation from inside, such as enjoyment'),
                    ('Extrinsic motivation', 'Motivation from outside, such as rewards'),
                    ('Growth mindset', 'Belief that abilities grow with effort and learning'),
                    ('Potential', 'What you are capable of becoming or achieving'),
                ],
                'example': {
                    'title': 'Class activity: fixed or growth?',
                    'html': (
                        '<p>Sort these statements into fixed mindset or growth mindset:</p>'
                        '<ul><li>"I\'ll never be good at this." (fixed)</li>'
                        '<li>"Mistakes help me learn." (growth)</li>'
                        '<li>"This is too hard, I give up." (fixed)</li>'
                        '<li>"I can\'t do it <em>yet</em>." (growth)</li>'
                        '<li>"Some people are just born clever." (fixed)</li></ul>'
                        '<p>Then rewrite each fixed statement as a growth statement.</p>'
                    ),
                },
                'video': {'id': 'KUWn_TJTrnU', 'title': 'Growth Mindset vs. Fixed Mindset',
                          'channel': 'Sprouts', 'minutes': 5},
                'worksheet': {
                    'instructions': 'Answer the questions and complete the plan.',
                    'exercises': [
                        '1. Define self-motivation.',
                        '2. Give one example each of intrinsic and extrinsic motivation from your own life.',
                        '3. What is the difference between a growth mindset and a fixed mindset?',
                        '4. Rewrite as a growth mindset statement: "I\'m not a reader."',
                        '5. List four strategies to stay motivated with schoolwork.',
                        '6. Choose one talent or skill you want to develop this year and write three steps to get there.',
                    ],
                },
                'quiz': [
                    ('mcq', 'Doing something because you enjoy it is:',
                     ['extrinsic motivation', 'intrinsic motivation', 'a fixed mindset', 'peer pressure'], 1),
                    ('tf', 'A person with a growth mindset sees mistakes as part of learning.', True),
                    ('mcq', 'Which statement shows a growth mindset?',
                     ['"I\'m just not smart."', '"I can\'t do it yet, but I\'m improving."',
                      '"Why try if I\'ll fail?"', '"Only talented people succeed."'], 1),
                    ('tf', 'Extrinsic motivation always lasts longer than intrinsic motivation.', False),
                ],
                'homework': {
                    'title': 'My potential plan',
                    'instructions': 'Make a one-page plan for the first term.',
                    'tasks': [
                        'Write one personal and one school goal for Term 1.',
                        'For each goal, list the steps, the support you need and how you will track progress.',
                        'Write how you will reward yourself when you reach each goal.',
                    ],
                    'marks': 15,
                },
            },
        ],
    },

    # ------------------------------------------------------------------ LO 9
    (9, 'LO'): {
        'topic': 'Development of the self in society: Goal-setting skills - personal lifestyle choices',
        'caps': 'Life Orientation Gr 9, Term 1, Development of the self in society: goal-setting skills - '
                'personal lifestyle choices; the influence of media, environment, friends and peers, '
                'family, culture, religion and community on personal lifestyle choices, and appropriate responses',
        'summary': 'Learners examine how lifestyle choices are influenced, practise responding '
                   'assertively to negative influences, and set SMART goals for a healthy lifestyle.',
        'days': [
            {
                'title': 'Personal lifestyle choices and what influences them',
                'minutes': 40,
                'objectives': [
                    'I can explain what a lifestyle choice is and give examples.',
                    'I can describe how media, peers, family, culture, religion and community influence choices.',
                    'I can link lifestyle choices to short- and long-term consequences.',
                ],
                'notes': (
                    '<p>A <strong>lifestyle</strong> is the way you live: what you eat, how active you are, how you sleep, '
                    'how you spend your time and money, who your friends are and whether you take risks such as smoking, '
                    'drinking or using drugs. Every day you make <strong>lifestyle choices</strong>, and together they '
                    'affect your health, relationships and future.</p>'
                    '<p><strong>Influences on lifestyle choices:</strong></p>'
                    '<ul><li><strong>Media and advertising:</strong> fast food, energy drinks, vapes and "influencers" are '
                    'marketed to teenagers as cool or normal.</li>'
                    '<li><strong>Friends and peers:</strong> the wish to belong can lead to positive habits (joining a '
                    'sports team) or risky ones.</li>'
                    '<li><strong>Family:</strong> family eating habits, routines, values and role modelling.</li>'
                    '<li><strong>Culture and religion:</strong> beliefs about food, alcohol, dress and behaviour.</li>'
                    '<li><strong>Environment and community:</strong> access to safe parks, healthy food, transport, '
                    'libraries, or exposure to crime and substances.</li></ul>'
                    '<p>Choices have <strong>consequences</strong>. Some show quickly (feeling tired after a late night); others '
                    'build up over years (diabetes from poor diet, lung disease from smoking). Thinking ahead helps you make '
                    'choices that match your goals and values.</p>'
                ),
                'key_terms': [
                    ('Lifestyle', 'The way a person lives, including habits and choices'),
                    ('Influence', 'The power to affect someone\'s choices'),
                    ('Consequence', 'The result of a choice or action'),
                    ('Values', 'Beliefs about what is important and right'),
                ],
                'example': {
                    'title': 'Class activity: influence analysis',
                    'html': (
                        '<p>Show (or describe) an advert for an energy drink aimed at teenagers.</p>'
                        '<ol><li>Who is the advert aimed at? How can you tell?</li>'
                        '<li>What message does it give (strength, popularity, success)?</li>'
                        '<li>What does it leave out (sugar, caffeine, effect on sleep)?</li>'
                        '<li>In groups, list one positive and one negative influence for each factor: media, peers, '
                        'family, culture/religion, community.</li></ol>'
                    ),
                },
                'video': {'id': 'soHn6t_jjIw', 'title': 'Impact of Social Media on Youth | Katanu Mbevi | TEDxYouth@BrookhouseSchool',
                          'channel': 'TEDx Talks', 'minutes': 12},
                'worksheet': {
                    'instructions': 'Answer in full sentences.',
                    'exercises': [
                        '1. What is a lifestyle? Name five lifestyle choices teenagers make every day.',
                        '2. Explain how advertising can influence a teenager\'s food or drink choices.',
                        '3. Give one positive and one negative example of peer influence.',
                        '4. How can a community environment make healthy choices easier or harder?',
                        '5. Give one short-term and one long-term consequence of regularly sleeping less than six hours.',
                        '6. How can your values help you make lifestyle choices?',
                    ],
                },
                'quiz': [
                    ('mcq', 'Which is a lifestyle choice?',
                     ['Your eye colour', 'Your height', 'How much exercise you do', 'Your date of birth'], 2),
                    ('tf', 'Advertising can influence what teenagers eat and drink.', True),
                    ('mcq', 'A long-term consequence of smoking is:',
                     ['bad breath today', 'lung disease', 'feeling cool', 'saving money'], 1),
                    ('tf', 'Peer influence is always negative.', False),
                ],
                'homework': {
                    'title': 'Lifestyle audit',
                    'instructions': 'Track your own choices for three days.',
                    'tasks': [
                        'Record your sleep, meals, physical activity and screen time for three days.',
                        'Identify the biggest influence on each area (media, peers, family, community, culture).',
                        'Choose one habit you would like to change and explain why.',
                    ],
                    'marks': 15,
                },
            },
            {
                'title': 'Responding to influences: assertiveness and refusal skills',
                'minutes': 40,
                'objectives': [
                    'I can tell the difference between passive, aggressive and assertive responses.',
                    'I can use refusal skills to say no to negative peer pressure.',
                    'I can identify sources of help and support.',
                ],
                'notes': (
                    '<p>You cannot control all influences, but you can control your <strong>response</strong>.</p>'
                    '<ul><li><strong>Passive:</strong> going along with others to avoid conflict, even when you do not want to.</li>'
                    '<li><strong>Aggressive:</strong> shouting, insulting or threatening others.</li>'
                    '<li><strong>Assertive:</strong> stating your view clearly, calmly and respectfully, while respecting others. '
                    'This is the healthiest response.</li></ul>'
                    '<p><strong>Refusal skills</strong> for negative peer pressure:</p>'
                    '<ol><li><strong>Say no clearly</strong> and mean it: "No, thanks."</li>'
                    '<li><strong>Give a reason</strong> (optional): "I have a match tomorrow."</li>'
                    '<li><strong>Suggest an alternative:</strong> "Let\'s go play soccer instead."</li>'
                    '<li><strong>Use strong body language:</strong> eye contact, firm voice.</li>'
                    '<li><strong>Walk away</strong> if the pressure continues.</li>'
                    '<li><strong>Stay with friends</strong> who share your values.</li></ol>'
                    '<p>Use the <strong>"I-statement"</strong>: "I feel uncomfortable when you push me to vape. I want you to '
                    'respect my choice."</p>'
                    '<p>If you need help, talk to a parent, teacher, counsellor or religious leader, or phone a helpline such '
                    'as Childline South Africa (116, toll-free).</p>'
                ),
                'key_terms': [
                    ('Assertive', 'Expressing yourself clearly and respectfully'),
                    ('Passive', 'Giving in to others and not expressing your needs'),
                    ('Aggressive', 'Forcing your view on others with anger or threats'),
                    ('Peer pressure', 'Influence from people your age to act in a certain way'),
                    ('Refusal skills', 'Ways to say no and stick to it'),
                ],
                'example': {
                    'title': 'Role-play: three ways to respond',
                    'html': (
                        '<p><strong>Scenario:</strong> At a party, a friend offers Sipho a drink of alcohol and says, '
                        '"Everyone\'s doing it. Don\'t be a baby."</p>'
                        '<p><strong>Passive:</strong> "Uh... okay, I guess." (takes it)</p>'
                        '<p><strong>Aggressive:</strong> "Get lost, you idiot!"</p>'
                        '<p><strong>Assertive:</strong> "No thanks, I don\'t drink. I\'m going to get a cooldrink - want one?"</p>'
                        '<p>In groups of three, act out a new scenario (skipping class, sharing someone\'s private photo, shoplifting) '
                        'with an assertive response.</p>'
                    ),
                },
                'video': {'id': 'SBaOUzFi_mI', 'title': 'What is the Right Way to Handle Peer Pressure - Wellness 101 Jr',
                          'channel': 'Glucose Guy', 'minutes': 4},
                'worksheet': {
                    'instructions': 'Answer the questions.',
                    'exercises': [
                        '1. Explain the difference between passive, aggressive and assertive behaviour.',
                        '2. List four refusal skills.',
                        '3. Write an assertive response to: "Come on, skip class with us, nobody will notice."',
                        '4. Write an I-statement for a friend who keeps pressuring you to share homework answers.',
                        '5. Why is it important to choose friends who share your values?',
                        '6. Name three people or organisations you could go to for help.',
                    ],
                },
                'quiz': [
                    ('mcq', 'Which response is assertive?',
                     ['"Fine, whatever you want."', '"Shut up or else!"',
                      '"No thanks, I\'m not interested. Let\'s do something else."', 'Saying nothing and leaving angrily'], 2),
                    ('tf', 'Suggesting an alternative activity is a refusal skill.', True),
                    ('mcq', 'Going along with others to avoid conflict, even when you disagree, is:',
                     ['assertive', 'passive', 'aggressive', 'respectful'], 1),
                    ('tf', 'Being assertive means you must shout to be heard.', False),
                ],
                'homework': {
                    'title': 'Refusal script',
                    'instructions': 'Prepare for real situations.',
                    'tasks': [
                        'Write a short dialogue (8-10 lines) in which a teenager uses three refusal skills.',
                        'Practise it with a family member and write one sentence about how it felt.',
                    ],
                    'marks': 10,
                },
            },
            {
                'title': 'Setting SMART goals for a healthy lifestyle',
                'minutes': 40,
                'objectives': [
                    'I can explain each part of a SMART goal.',
                    'I can turn a vague goal into a SMART goal.',
                    'I can write an action plan for a personal lifestyle goal.',
                ],
                'notes': (
                    '<p>A <strong>goal</strong> is something you want to achieve. Goals give direction to your choices. '
                    '<strong>Short-term goals</strong> can be reached in days or weeks; <strong>long-term goals</strong> take months or years.</p>'
                    '<p>Strong goals are <strong>SMART</strong>:</p>'
                    '<ul><li><strong>S - Specific:</strong> clear and exact. Not "get fit" but "jog".</li>'
                    '<li><strong>M - Measurable:</strong> you can track it: "for 20 minutes, three times a week".</li>'
                    '<li><strong>A - Achievable:</strong> possible with your time and resources.</li>'
                    '<li><strong>R - Realistic / Relevant:</strong> it matters to you and fits your life.</li>'
                    '<li><strong>T - Time-bound:</strong> it has a deadline: "by the end of Term 1".</li></ul>'
                    '<p><strong>Example:</strong> Vague: "I want to eat better." SMART: "I will replace fizzy drinks with water '
                    'on school days for the next six weeks, and record it on a chart."</p>'
                    '<p><strong>Action plan steps:</strong> write the goal; list the steps; identify possible obstacles '
                    '(friends, cost, time) and how to overcome them; name your support (family, friend, coach); decide how to '
                    'track progress; and review and adjust the goal regularly. Celebrate progress, not only the final result.</p>'
                ),
                'key_terms': [
                    ('Goal', 'Something you aim to achieve'),
                    ('SMART', 'Specific, Measurable, Achievable, Realistic, Time-bound'),
                    ('Action plan', 'The steps you will take to reach a goal'),
                    ('Obstacle', 'Something that could stop you from reaching a goal'),
                ],
                'example': {
                    'title': 'Worked example: making a goal SMART',
                    'html': (
                        '<p><strong>Vague goal:</strong> "I want to sleep more."</p>'
                        '<p><strong>S:</strong> go to bed earlier on school nights.</p>'
                        '<p><strong>M:</strong> lights out by 21:30 and phone off by 21:00, recorded in a sleep diary.</p>'
                        '<p><strong>A:</strong> yes - homework is usually done by 20:30.</p>'
                        '<p><strong>R:</strong> I feel tired in first period, and sleep helps concentration.</p>'
                        '<p><strong>T:</strong> for the next four weeks, then review.</p>'
                        '<p><strong>SMART goal:</strong> "For the next four weeks, I will switch off my phone at 21:00 and be '
                        'in bed by 21:30 on school nights, and record it in a sleep diary."</p>'
                    ),
                },
                'video': {'id': 'i0QfCZjASX8', 'title': 'How to Set SMART Goals | Goal Setting for Students',
                          'channel': '2 Minute Classroom', 'minutes': 3},
                'worksheet': {
                    'instructions': 'Complete the exercises.',
                    'exercises': [
                        '1. What does each letter in SMART stand for?',
                        '2. What is the difference between a short-term and a long-term goal?',
                        '3. Rewrite as a SMART goal: "I want to be healthier."',
                        '4. Rewrite as a SMART goal: "I want to spend less time on my phone."',
                        '5. Name two possible obstacles to a fitness goal and how you would overcome them.',
                        '6. Why is it useful to track and review your progress?',
                    ],
                },
                'quiz': [
                    ('mcq', 'In SMART, the "T" stands for:',
                     ['Tough', 'Time-bound', 'Tested', 'Together'], 1),
                    ('mcq', 'Which goal is the most SMART?',
                     ['"I will get fit."', '"I will exercise more sometimes."',
                      '"I will walk for 30 minutes on 4 days a week until 31 March."', '"I want to be a better person."'], 2),
                    ('tf', 'Identifying obstacles is part of a good action plan.', True),
                    ('tf', 'A measurable goal cannot be tracked.', False),
                ],
                'homework': {
                    'title': 'My healthy lifestyle goal',
                    'instructions': 'Use your lifestyle audit from Day 1.',
                    'tasks': [
                        'Write one SMART goal to improve your lifestyle this term.',
                        'Write an action plan with steps, obstacles, support and a tracking method.',
                        'Design a simple chart to track your progress for four weeks.',
                    ],
                    'marks': 20,
                },
            },
        ],
    },

    # ------------------------------------------------------------------ CODING 7
    (7, 'CODING'): {
        'topic': 'Algorithms and coding: algorithms, flowcharts and block-based coding',
        'caps': 'Coding and Robotics Gr 7, Term 1: Algorithms and coding - computational thinking '
                '(decomposition, sequencing), writing algorithms, representing algorithms as '
                'flowcharts, and introduction to block-based coding',
        'summary': 'Learners write precise step-by-step algorithms, represent them as flowcharts '
                   'with standard symbols, and turn an algorithm into a simple block-based program.',
        'days': [
            {
                'title': 'What is an algorithm?',
                'minutes': 45,
                'objectives': [
                    'I can define an algorithm.',
                    'I can break a task into smaller steps (decomposition).',
                    'I can write a clear, precise algorithm in the correct sequence.',
                ],
                'notes': (
                    '<p>An <strong>algorithm</strong> is a set of clear, step-by-step instructions to complete a task or solve '
                    'a problem. A recipe, directions to a friend\'s house and the steps for long division are all algorithms. '
                    'Computers need algorithms because they do <em>exactly</em> what they are told - nothing more, nothing less.</p>'
                    '<p><strong>Computational thinking</strong> helps us create algorithms:</p>'
                    '<ul><li><strong>Decomposition:</strong> break a big problem into smaller parts.</li>'
                    '<li><strong>Pattern recognition:</strong> look for steps that repeat.</li>'
                    '<li><strong>Abstraction:</strong> focus on the important details and ignore the rest.</li>'
                    '<li><strong>Algorithm design:</strong> write the steps in order.</li></ul>'
                    '<p><strong>A good algorithm is:</strong></p>'
                    '<ul><li><strong>Precise</strong> - each step is clear and cannot be misunderstood.</li>'
                    '<li><strong>In sequence</strong> - the order is correct (you cannot put on shoes before socks).</li>'
                    '<li><strong>Finite</strong> - it has a clear start and end.</li></ul>'
                    '<p>A mistake in an algorithm or program is called a <strong>bug</strong>; finding and fixing it is '
                    '<strong>debugging</strong>.</p>'
                ),
                'key_terms': [
                    ('Algorithm', 'A precise, step-by-step set of instructions'),
                    ('Sequence', 'The order in which steps are carried out'),
                    ('Decomposition', 'Breaking a problem into smaller parts'),
                    ('Bug', 'An error in an algorithm or program'),
                    ('Debugging', 'Finding and fixing errors'),
                ],
                'example': {
                    'title': 'Class activity: program the teacher',
                    'html': (
                        '<p>The teacher acts as a "robot" who follows instructions <em>exactly</em>.</p>'
                        '<ol><li>Learners give instructions to make a jam sandwich (bread, jam, knife on the desk).</li>'
                        '<li>The "robot" follows each instruction literally (e.g. "put jam on the bread" - puts the closed jar on the bread!).</li>'
                        '<li>Learners debug: rewrite the instructions more precisely.</li></ol>'
                        '<p>Final algorithm example: 1. Open the bag. 2. Take out two slices. 3. Unscrew the jar lid. '
                        '4. Use the knife to scoop jam. 5. Spread jam on one slice. 6. Place the second slice on top.</p>'
                    ),
                },
                'video': {'id': 'SiTSq2h1EaQ', 'title': 'What is an Algorithm? | All About Computers | Tynker',
                          'channel': 'Tynker', 'minutes': 3},
                'worksheet': {
                    'instructions': 'Answer the questions and write the algorithms.',
                    'exercises': [
                        '1. Define an algorithm in your own words.',
                        '2. Give three examples of algorithms in everyday life.',
                        '3. Write an algorithm (at least six steps) for brushing your teeth.',
                        '4. These steps are out of order. Put them in sequence: dry hands, turn off tap, wet hands, rinse, use soap.',
                        '5. What is decomposition? Break "planning a class party" into four smaller tasks.',
                        '6. What is a bug, and what is debugging?',
                    ],
                },
                'quiz': [
                    ('mcq', 'An algorithm is:',
                     ['a type of computer', 'a step-by-step set of instructions', 'a programming error', 'a robot part'], 1),
                    ('tf', 'Breaking a big problem into smaller parts is called decomposition.', True),
                    ('mcq', 'Fixing a mistake in a program is called:',
                     ['coding', 'sequencing', 'debugging', 'decomposing'], 2),
                    ('tf', 'The order of the steps in an algorithm does not matter.', False),
                ],
                'homework': {
                    'title': 'Algorithms at home',
                    'instructions': 'Write and test an algorithm with someone at home.',
                    'tasks': [
                        'Write an algorithm of 8-10 steps for a daily task (making tea, tying shoelaces, packing your bag).',
                        'Ask a family member to follow it exactly. Record any bugs and write the corrected version.',
                    ],
                    'marks': 10,
                },
            },
            {
                'title': 'Flowcharts: drawing algorithms',
                'minutes': 45,
                'objectives': [
                    'I can identify standard flowchart symbols.',
                    'I can draw a flowchart for a simple sequence.',
                    'I can include a decision (yes/no) in a flowchart.',
                ],
                'notes': (
                    '<p>A <strong>flowchart</strong> is a diagram that shows the steps of an algorithm using shapes joined by '
                    'arrows. It makes the flow of an algorithm easy to follow.</p>'
                    '<p><strong>Standard flowchart symbols:</strong></p>'
                    '<ul><li><strong>Oval (terminator):</strong> Start and End.</li>'
                    '<li><strong>Rectangle (process):</strong> an action or instruction, e.g. "Boil water".</li>'
                    '<li><strong>Parallelogram (input/output):</strong> getting or showing information, e.g. "Enter a number" or '
                    '"Display the answer".</li>'
                    '<li><strong>Diamond (decision):</strong> a yes/no question, e.g. "Is it raining?". It has two arrows '
                    'out: Yes and No.</li>'
                    '<li><strong>Arrows (flow lines):</strong> show the direction to follow.</li></ul>'
                    '<p><strong>Decisions</strong> let an algorithm choose a path (this is called <em>selection</em>). '
                    'Arrows can also loop back to an earlier step to repeat it (called a <em>loop</em> or '
                    '<em>iteration</em>), for example "Is the glass full? No - pour more water."</p>'
                    '<p>Rules: start with one Start and finish with End; arrows show flow from top to bottom; every decision '
                    'needs both a Yes and a No path.</p>'
                ),
                'key_terms': [
                    ('Flowchart', 'A diagram of an algorithm using shapes and arrows'),
                    ('Process', 'An action step, drawn as a rectangle'),
                    ('Decision', 'A yes/no question, drawn as a diamond'),
                    ('Input/output', 'Data in or out, drawn as a parallelogram'),
                    ('Loop', 'Repeating steps until a condition is met'),
                ],
                'example': {
                    'title': 'Worked example: should I take an umbrella?',
                    'html': (
                        '<ol><li><strong>Start</strong> (oval)</li>'
                        '<li><strong>Look outside</strong> (rectangle)</li>'
                        '<li><strong>Is it raining?</strong> (diamond)<br>'
                        'Yes: <strong>Take an umbrella</strong> (rectangle), then go to step 4.<br>'
                        'No: go straight to step 4.</li>'
                        '<li><strong>Walk to school</strong> (rectangle)</li>'
                        '<li><strong>End</strong> (oval)</li></ol>'
                        '<p>Draw this on the board with the correct shapes and arrows.</p>'
                    ),
                },
                'video': {'id': 'Zu_YXl7CaZM', 'title': 'Flowchart in Computer Science | Symbols & Their Uses | Easy Explanation',
                          'channel': "Let's Learn CS", 'minutes': 5},
                'worksheet': {
                    'instructions': 'Draw neatly with a ruler and pencil.',
                    'exercises': [
                        '1. Draw and name the four main flowchart symbols.',
                        '2. Which symbol is used for a yes/no question?',
                        '3. Draw a flowchart for making a cup of tea (at least five steps).',
                        '4. Draw a flowchart that asks "Is the traffic light green?" and decides whether to cross or wait.',
                        '5. What is a loop? Add a loop to question 4 so that you wait until the light is green.',
                        '6. Find and correct the error: a flowchart has a decision diamond with only a "Yes" arrow.',
                    ],
                },
                'quiz': [
                    ('mcq', 'Which shape is used for a decision in a flowchart?',
                     ['Oval', 'Rectangle', 'Diamond', 'Parallelogram'], 2),
                    ('mcq', 'Start and End are shown with a(n):',
                     ['oval', 'diamond', 'rectangle', 'circle with a cross'], 0),
                    ('tf', 'A decision symbol must have both a Yes and a No path.', True),
                    ('tf', 'Parallelograms are used to show the start of a flowchart.', False),
                ],
                'homework': {
                    'title': 'My morning flowchart',
                    'instructions': 'Use correct flowchart symbols.',
                    'tasks': [
                        'Draw a flowchart of your morning routine from waking up to leaving home.',
                        'Include at least one decision (e.g. "Is my bag packed?") and one loop.',
                    ],
                    'marks': 15,
                },
            },
            {
                'title': 'From algorithm to code: block-based programming',
                'minutes': 45,
                'objectives': [
                    'I can explain what block-based coding is.',
                    'I can use event, motion and looks blocks in sequence.',
                    'I can use a repeat (loop) block to make code shorter.',
                ],
                'notes': (
                    '<p><strong>Coding (programming)</strong> means writing instructions in a language a computer understands. '
                    'A <strong>program</strong> is an algorithm written in code.</p>'
                    '<p><strong>Block-based coding</strong> (for example <strong>Scratch</strong> or <strong>Code.org</strong>) uses '
                    'coloured blocks that snap together like puzzle pieces, so you can focus on logic instead of typing '
                    'and spelling.</p>'
                    '<p><strong>Key parts of Scratch:</strong></p>'
                    '<ul><li><strong>Sprite</strong> - a character or object that the code controls (e.g. the cat).</li>'
                    '<li><strong>Stage</strong> - the background where the sprites move.</li>'
                    '<li><strong>Events blocks</strong> (yellow) start code, e.g. "when green flag clicked".</li>'
                    '<li><strong>Motion blocks</strong> (blue) move a sprite: "move 10 steps", "turn 90 degrees".</li>'
                    '<li><strong>Looks blocks</strong> (purple): "say Hello! for 2 seconds".</li>'
                    '<li><strong>Control blocks</strong> (orange): "repeat 4", "forever", "wait 1 second", "if...then".</li></ul>'
                    '<p>Code runs from <strong>top to bottom</strong>, in sequence. A <strong>repeat (loop)</strong> block runs the '
                    'blocks inside it several times, which saves writing the same blocks again and again. If the program does '
                    'not do what you expect, <strong>debug</strong> it one block at a time.</p>'
                ),
                'key_terms': [
                    ('Program', 'An algorithm written in a coding language'),
                    ('Block-based coding', 'Coding by snapping visual blocks together'),
                    ('Sprite', 'A character or object controlled by code in Scratch'),
                    ('Event', 'Something that starts the code, like clicking the green flag'),
                    ('Loop', 'A block that repeats the code inside it'),
                ],
                'example': {
                    'title': 'Worked example: draw a square in Scratch',
                    'html': (
                        '<p><strong>Algorithm:</strong> move forward, turn right 90°, repeat 4 times.</p>'
                        '<p><strong>Long version (no loop):</strong><br>'
                        'when green flag clicked<br>pen down<br>move 100 steps<br>turn 90 degrees<br>'
                        'move 100 steps<br>turn 90 degrees<br>move 100 steps<br>turn 90 degrees<br>move 100 steps<br>turn 90 degrees</p>'
                        '<p><strong>Short version (with a loop):</strong><br>'
                        'when green flag clicked<br>pen down<br>repeat 4<br>... move 100 steps<br>... turn 90 degrees</p>'
                        '<p>Challenge: change the code to draw a triangle (repeat 3, turn 120 degrees).</p>'
                    ),
                },
                'video': {'id': 'sb-wF35TuvQ',
                          'title': 'Scratch Tutorial | Introduction to Scratch | Part 1 | Scratch Easy Beginner Tutorial',
                          'channel': 'Kids Coding Playground', 'minutes': 8},
                'worksheet': {
                    'instructions': 'Answer the questions. If you have a device, test your code in Scratch.',
                    'exercises': [
                        '1. What is the difference between an algorithm and a program?',
                        '2. Why is block-based coding good for beginners?',
                        '3. What is a sprite? What is the stage?',
                        '4. Which block would you use to start a program when the green flag is clicked?',
                        '5. Write the blocks to make a sprite say "Hello!" and then move 50 steps.',
                        '6. Use a repeat block to draw a square. How many times does it repeat, and how many degrees does it turn?',
                        '7. How would you change the square code to draw a triangle?',
                    ],
                },
                'quiz': [
                    ('mcq', 'In Scratch, a character controlled by code is called a:',
                     ['stage', 'sprite', 'block', 'loop'], 1),
                    ('mcq', 'To draw a square with a repeat block, you repeat 4 times and turn:',
                     ['45 degrees', '120 degrees', '90 degrees', '180 degrees'], 2),
                    ('tf', 'Code in Scratch runs from top to bottom in sequence.', True),
                    ('tf', 'A loop makes code longer because blocks must be written out again.', False),
                ],
                'homework': {
                    'title': 'Code a shape',
                    'instructions': 'Use Scratch (scratch.mit.edu) if you have access, or write the blocks on paper.',
                    'tasks': [
                        'Write the code to draw a triangle using a repeat block.',
                        'Write the code to draw a hexagon (6 sides). Work out the turning angle (360 / 6).',
                        'Draw the flowchart for your hexagon code.',
                    ],
                    'marks': 15,
                },
            },
        ],
    },
}
