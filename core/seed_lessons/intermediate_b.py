"""Intermediate Phase (part B): Term 1, Week 1 demo lessons, Grades 4-6.

Offerings (12):
    (4, 'NST'), (5, 'NST'), (6, 'NST')              Natural Sciences and Technology
    (4, 'SOC-SCI'), (5, 'SOC-SCI'), (6, 'SOC-SCI')  Social Sciences (Geography strand)
    (4, 'LIFE-SK'), (5, 'LIFE-SK'), (6, 'LIFE-SK')  Life Skills (Personal and Social Well-being)
    (4, 'CODING'), (5, 'CODING'), (6, 'CODING')     Coding and Robotics

CAPS sources used:
    - CAPS Natural Sciences and Technology, Intermediate Phase Gr 4-6 (DBE 2011), Strand
      Life and Living, Term 1: Gr 4 "Living and non-living things"; Gr 5 "Plants and
      animals on Earth"; Gr 6 "Photosynthesis" (first topic before "Nutrients in food").
    - CAPS Social Sciences, Intermediate Phase Gr 4-6 (DBE 2011) and the DBE / WCED Annual
      Teaching Plans for Social Sciences Gr 4-6 Term 1: Geography Gr 4 "Places where people
      live"; Gr 5 "Map skills"; Gr 6 "Map skills" (latitude and longitude). Week 1 is
      written on the Geography strand of Term 1.
    - CAPS Life Skills, Intermediate Phase Gr 4-6 (DBE 2011), Term 1 Personal and Social
      Well-being: "Development of the self" (personal strengths, positive self-concept,
      respecting differences, emotions).
    - DBE Coding and Robotics draft CAPS, Gr 4-6 (2021 pilot): pattern recognition,
      algorithms and sequencing (unplugged), debugging, block-based coding (Scratch),
      events and loops, robotics basics (input, process, output).
"""

LESSONS = {
    # ------------------------------------------------------------------ NST
    (4, 'NST'): {
        'topic': 'Living and non-living things',
        'caps': 'Life and Living: Living and non-living things - features of living things '
                '(the seven life processes); things that are alive, were once alive and were never alive',
        'summary': 'Learners find out what makes something alive, learn the seven life processes '
                   'and sort things into living, once-living and non-living groups.',
        'days': [
            {
                'title': 'What makes something alive?',
                'minutes': 45,
                'objectives': [
                    'I can explain the difference between living and non-living things.',
                    'I can give examples of living and non-living things in my surroundings.',
                    'I can say why a plant is a living thing.',
                ],
                'notes': (
                    '<p>Everything around us is either <strong>living</strong> or <strong>non-living</strong>. '
                    'Living things are also called <strong>organisms</strong>. People, dogs, trees, grass, '
                    'mushrooms and even tiny ants are living things.</p>'
                    '<p>How do we know something is alive? Living things do certain things that non-living '
                    'things cannot do. A living thing:</p>'
                    '<ul><li>needs food and water,</li><li>grows and changes,</li>'
                    '<li>breathes (takes in and gives out air),</li><li>can produce young (reproduce),</li>'
                    '<li>reacts to what happens around it,</li><li>and in the end it dies.</li></ul>'
                    '<p>A rock, a chair, a pencil and water are <strong>non-living</strong>. They do not eat, '
                    'grow or reproduce. Be careful: some non-living things <em>seem</em> alive. A car moves '
                    'and uses fuel, and a fire "grows", but they cannot reproduce and they do not grow by '
                    'themselves from inside.</p>'
                    '<p>Plants are living even though they do not walk around. They grow, make seeds, need '
                    'water and turn their leaves towards the light.</p>'
                ),
                'key_terms': [
                    ('living thing', 'something that is alive: it feeds, grows, breathes and reproduces'),
                    ('non-living thing', 'something that is not alive and never was'),
                    ('organism', 'another word for a living thing'),
                ],
                'example': {
                    'title': 'Class activity: alive or not?',
                    'html': (
                        '<p>Walk around the classroom or school grounds with a partner. Make a list of '
                        '10 things you see.</p>'
                        '<ol><li>Next to each thing write L (living) or N (non-living).</li>'
                        '<li>For one living thing, give two reasons why you know it is alive.</li>'
                        '<li>For one non-living thing, give one reason why it is not alive.</li></ol>'
                        '<p><em>Example:</em> Tree - L, because it grows and makes seeds. '
                        'Desk - N, because it does not eat or grow.</p>'
                    ),
                },
                'video': {'id': 'za5z6WRz29I',
                          'title': 'Living & Non Living Things | What Are Non Living Things? | The Dr Binocs Show | Peekaboo Kidz',
                          'channel': 'Peekaboo Kidz', 'minutes': 5},
                'worksheet': {
                    'instructions': 'Write L for living or N for non-living next to each thing. Then answer the last two questions in full sentences.',
                    'exercises': [
                        '1. A goat ____',
                        '2. A stone ____',
                        '3. A mielie plant ____',
                        '4. A bicycle ____',
                        '5. A spider ____',
                        '6. A cloud ____',
                        '7. Give two reasons why a cat is a living thing.',
                        '8. A car moves and needs fuel. Explain why it is still non-living.',
                    ],
                },
                'quiz': [
                    ('mcq', 'Which of these is a living thing?', ['A rock', 'A tree', 'A chair', 'A spoon'], 1),
                    ('tf', 'Plants are living things because they grow and make seeds.', True),
                    ('tf', 'A car is a living thing because it moves.', False),
                    ('mcq', 'Which is another word for a living thing?', ['Mineral', 'Machine', 'Organism'], 2),
                ],
                'homework': {
                    'title': 'Living and non-living at home',
                    'instructions': 'Look around your home and garden. Find living and non-living things.',
                    'tasks': [
                        'List 5 living things and 5 non-living things you find at home.',
                        'Choose one living thing from your list and write two sentences explaining how you know it is alive.',
                    ],
                    'marks': 10,
                },
            },
            {
                'title': 'The seven life processes',
                'minutes': 45,
                'objectives': [
                    'I can name the seven life processes.',
                    'I can describe each life process in my own words.',
                    'I can show how a plant and an animal carry out the same life processes.',
                ],
                'notes': (
                    '<p>Scientists say something is alive if it carries out <strong>all seven life '
                    'processes</strong>. Many learners remember them with the name <strong>MRS GREN</strong>:</p>'
                    '<ul>'
                    '<li><strong>M - Movement:</strong> living things move. Animals walk, swim or fly; plants '
                    'move slowly, for example leaves turn towards the sun.</li>'
                    '<li><strong>R - Respiration (breathing):</strong> living things use air to get energy from food.</li>'
                    '<li><strong>S - Sensitivity:</strong> living things notice and react to changes, like '
                    'light, heat, sound or touch.</li>'
                    '<li><strong>G - Growth:</strong> living things grow bigger and change.</li>'
                    '<li><strong>R - Reproduction:</strong> living things make young ones like themselves. '
                    'Plants make seeds; animals have babies or lay eggs.</li>'
                    '<li><strong>E - Excretion:</strong> living things get rid of waste.</li>'
                    '<li><strong>N - Nutrition (feeding):</strong> living things need food. Animals eat food; '
                    'plants make their own food using sunlight.</li>'
                    '</ul>'
                    '<p>A thing must do <em>all seven</em> to be called alive. A fire may "move", "grow" and '
                    'need air, but it does not reproduce or get rid of waste like a living thing, so it is non-living.</p>'
                ),
                'key_terms': [
                    ('life processes', 'the seven things all living things do'),
                    ('respiration', 'using air (oxygen) to release energy from food'),
                    ('sensitivity', 'noticing and reacting to changes around you'),
                    ('excretion', 'getting rid of waste from the body'),
                    ('reproduction', 'making young ones'),
                ],
                'example': {
                    'title': 'Worked example: a bean plant and a dog',
                    'html': (
                        '<p>Compare how a bean plant and a dog carry out three life processes:</p>'
                        '<ul>'
                        '<li><strong>Nutrition:</strong> the dog eats food; the bean plant makes its own food in its leaves.</li>'
                        '<li><strong>Sensitivity:</strong> the dog runs when it hears its name; the bean plant bends towards the window light.</li>'
                        '<li><strong>Reproduction:</strong> the dog has puppies; the bean plant makes new beans (seeds).</li>'
                        '</ul>'
                        '<p>Both do all seven processes, so both are living.</p>'
                    ),
                },
                'video': {'id': 'jpO52VTHecQ',
                          'title': 'Seven Life Processes | Physiology | Biology | FuseSchool',
                          'channel': 'FuseSchool - Global Education', 'minutes': 4},
                'worksheet': {
                    'instructions': 'Match each life process to its meaning, then answer the questions.',
                    'exercises': [
                        '1. Write out what each letter of MRS GREN stands for.',
                        '2. Which life process is happening when a baby grows taller?',
                        '3. Which life process is happening when you pull your hand away from a hot pot?',
                        '4. Which life process is happening when a hen lays eggs?',
                        '5. How does a plant get its food (nutrition)?',
                        '6. Give one example of how a plant moves.',
                        '7. A fire uses air and gets bigger. Name one life process a fire cannot do.',
                    ],
                },
                'quiz': [
                    ('mcq', 'How many life processes are there?', ['Five', 'Six', 'Seven', 'Ten'], 2),
                    ('mcq', 'Getting rid of waste from the body is called ...', ['excretion', 'growth', 'nutrition'], 0),
                    ('tf', 'Plants do not carry out any movement at all.', False),
                    ('mcq', 'A cat jumps when it hears a loud noise. Which life process is this?',
                     ['Reproduction', 'Sensitivity', 'Respiration', 'Growth'], 1),
                    ('tf', 'To be alive, something must carry out all seven life processes.', True),
                ],
                'homework': {
                    'title': 'MRS GREN poster',
                    'instructions': 'Make a small poster (on an A4 page) about the seven life processes.',
                    'tasks': [
                        'Write MRS GREN down the side of the page and the name of each life process next to its letter.',
                        'Draw or describe one example for each life process, using a person, an animal or a plant.',
                    ],
                    'marks': 14,
                },
            },
            {
                'title': 'Sorting: living, once-living and non-living',
                'minutes': 45,
                'objectives': [
                    'I can sort things into living, once-living (dead) and non-living groups.',
                    'I can explain why a thing belongs in a group.',
                    'I can record my sorting in a table.',
                ],
                'notes': (
                    '<p>Scientists <strong>sort</strong> (classify) things into groups so that they are '
                    'easier to study. Today we use <strong>three</strong> groups:</p>'
                    '<ol>'
                    '<li><strong>Living</strong> - alive now and carrying out the seven life processes, e.g. a lizard, a rose bush.</li>'
                    '<li><strong>Once-living (dead)</strong> - was alive before but has died, or is a part '
                    'that came from a living thing, e.g. a dry leaf, a wooden spoon, a bone, cotton, a feather.</li>'
                    '<li><strong>Never living (non-living)</strong> - was never alive, e.g. a stone, glass, metal, water, air.</li>'
                    '</ol>'
                    '<p>A wooden table is <em>once-living</em> because wood comes from a tree. Paper also comes '
                    'from trees. Leather comes from animal skin. These things cannot grow or feed any more, '
                    'but they came from living things.</p>'
                    '<p>Seeds are interesting: a dry bean seed looks dead, but it is <strong>living</strong>. '
                    'If you give it water and warmth it will grow into a new plant.</p>'
                    '<p>When you sort, always give a <strong>reason</strong> for your choice. This is how scientists work.</p>'
                ),
                'key_terms': [
                    ('classify', 'to sort things into groups by what they have in common'),
                    ('once-living', 'was alive before, or came from a living thing, but is now dead'),
                    ('never living', 'was never alive, e.g. rock, metal, glass'),
                ],
                'example': {
                    'title': 'Guided activity: sorting table',
                    'html': (
                        '<p>Draw a table with three columns: <strong>Living</strong>, <strong>Once-living</strong>, '
                        '<strong>Never living</strong>. Sort these items: earthworm, newspaper, stone, '
                        'chicken, feather, glass bottle, grass, wooden ruler, metal key.</p>'
                        '<p><em>Answer:</em> Living - earthworm, chicken, grass. Once-living - newspaper, '
                        'feather, wooden ruler. Never living - stone, glass bottle, metal key.</p>'
                    ),
                },
                'video': {'id': 'kBL9-RFhnbM',
                          'title': 'Living and Non-living Things for Kids | Learn why some things are alive and others are not',
                          'channel': 'Learn Bright', 'minutes': 10},
                'worksheet': {
                    'instructions': 'Draw a table with three columns: Living, Once-living, Never living. Write each item in the correct column and answer the questions.',
                    'exercises': [
                        '1. Sort: cow, leather shoe, plastic cup, sunflower, cardboard box, sand.',
                        '2. Sort: butterfly, cotton T-shirt, iron nail, fern, eggshell, water.',
                        '3. Why is a wooden chair in the once-living group?',
                        '4. A dry bean seed looks dead. Is it living? Explain.',
                        '5. Name two things in your classroom that were once living.',
                        '6. Name two things that have never been alive.',
                    ],
                },
                'quiz': [
                    ('mcq', 'A wooden spoon is ...', ['living', 'once-living', 'never living'], 1),
                    ('mcq', 'Which of these has never been alive?', ['A feather', 'A piece of paper', 'A metal key', 'A dry leaf'], 2),
                    ('tf', 'A seed can be living even though it does not seem to do anything.', True),
                    ('tf', 'Leather is never living because it is used to make shoes.', False),
                ],
                'homework': {
                    'title': 'My sorting collection',
                    'instructions': 'Find small, safe objects at home (or draw them) for each group.',
                    'tasks': [
                        'Find or draw 3 living, 3 once-living and 3 never-living things.',
                        'Write one sentence for each group explaining why the things belong there.',
                    ],
                    'marks': 12,
                },
            },
        ],
    },
    (5, 'NST'): {
        'topic': 'Plants and animals on Earth',
        'caps': 'Life and Living: Plants and animals on Earth - many different plants and animals; '
                'habitats; interdependence of plants and animals',
        'summary': 'Learners explore the huge variety of plants and animals on Earth, the habitats they '
                   'live in and how living things depend on one another.',
        'days': [
            {
                'title': 'Many different plants and animals',
                'minutes': 45,
                'objectives': [
                    'Learners will explain what biodiversity means.',
                    'Learners will give examples of the variety of plants and animals in South Africa.',
                    'Learners will group animals by simple features such as body covering or number of legs.',
                ],
                'notes': (
                    '<p>Earth has millions of different kinds of plants and animals. Each kind is called a '
                    '<strong>species</strong>. The variety of all living things in an area is called '
                    '<strong>biodiversity</strong>.</p>'
                    '<p>South Africa has very rich biodiversity. The fynbos of the Western Cape has thousands '
                    'of plant species, such as proteas and ericas. Our savannas are home to lions, elephants, '
                    'giraffes and many birds. Our oceans have sharks, dolphins, penguins and seaweeds.</p>'
                    '<p>Plants can be very different from each other:</p>'
                    '<ul><li>huge trees like the baobab and tiny mosses,</li>'
                    '<li>plants with flowers (sunflowers, aloes) and plants without flowers (ferns, mosses),</li>'
                    '<li>plants that store water, like succulents and cacti, in dry places.</li></ul>'
                    '<p>Animals also vary. Some have <strong>backbones</strong> (vertebrates), such as fish, '
                    'frogs, snakes, birds and mammals. Others have <strong>no backbone</strong> (invertebrates), '
                    'such as insects, spiders, worms and snails. We can also group animals by their body '
                    'covering: fur or hair, feathers, scales or smooth moist skin.</p>'
                    '<p>Biodiversity is important because living things provide us with food, medicine, '
                    'clean air and water.</p>'
                ),
                'key_terms': [
                    ('species', 'one particular kind of plant or animal'),
                    ('biodiversity', 'the variety of living things in an area'),
                    ('vertebrate', 'an animal with a backbone'),
                    ('invertebrate', 'an animal without a backbone'),
                ],
                'example': {
                    'title': 'Guided activity: group the animals',
                    'html': (
                        '<p>Group these animals by body covering: cat, eagle, crocodile, frog, sheep, ostrich, snake, dog.</p>'
                        '<ul><li><strong>Fur/hair:</strong> cat, sheep, dog</li>'
                        '<li><strong>Feathers:</strong> eagle, ostrich</li>'
                        '<li><strong>Scales:</strong> crocodile, snake</li>'
                        '<li><strong>Smooth, moist skin:</strong> frog</li></ul>'
                        '<p>Now try another way: group them by number of legs (0, 2 or 4).</p>'
                    ),
                },
                'video': {'id': 'zU-oB6XzE18', 'title': 'Biodiversity | Science for Kids',
                          'channel': 'Little School', 'minutes': 4},
                'worksheet': {
                    'instructions': 'Answer the questions in full sentences.',
                    'exercises': [
                        '1. What does the word biodiversity mean?',
                        '2. Name three plants and three animals that live in South Africa.',
                        '3. Give one difference between a fern and a sunflower.',
                        '4. Sort into vertebrates and invertebrates: beetle, frog, snail, lizard, earthworm, owl.',
                        '5. Group by body covering: zebra, hen, python, toad, goat.',
                        '6. Give two reasons why biodiversity is important to people.',
                    ],
                },
                'quiz': [
                    ('mcq', 'The variety of living things in an area is called ...', ['habitat', 'biodiversity', 'weather', 'soil'], 1),
                    ('mcq', 'Which animal is an invertebrate?', ['Frog', 'Snake', 'Spider', 'Eagle'], 2),
                    ('tf', 'Ferns and mosses are plants that do not make flowers.', True),
                    ('mcq', 'Which body covering do birds have?', ['Feathers', 'Scales', 'Fur'], 0),
                ],
                'homework': {
                    'title': 'Living things around me',
                    'instructions': 'Look carefully in your garden, a park or on the way home.',
                    'tasks': [
                        'List 4 different plants and 4 different animals (including insects) that you saw.',
                        'Put a V next to each vertebrate and an I next to each invertebrate.',
                        'Describe the most unusual living thing you saw in two sentences.',
                    ],
                    'marks': 12,
                },
            },
            {
                'title': 'Habitats: where plants and animals live',
                'minutes': 45,
                'objectives': [
                    'Learners will define a habitat.',
                    'Learners will describe what a habitat provides for living things.',
                    'Learners will explain how plants and animals are suited to their habitats.',
                ],
                'notes': (
                    '<p>A <strong>habitat</strong> is the place where a plant or animal lives. A good habitat '
                    'gives living things what they need to survive:</p>'
                    '<ul><li><strong>food</strong> and <strong>water</strong>,</li>'
                    '<li><strong>shelter</strong> (a safe place to rest and hide),</li>'
                    '<li><strong>air</strong> and the right temperature,</li>'
                    '<li>a place to <strong>reproduce</strong> and raise young.</li></ul>'
                    '<p>Habitats can be big, like a forest, grassland, desert or ocean, or small, like a rotting '
                    'log, a pond or the underside of a rock.</p>'
                    '<p>Living things have features that suit them to their habitat. We say they are '
                    '<strong>adapted</strong>. For example:</p>'
                    '<ul><li>In the dry Karoo, succulent plants store water in thick leaves.</li>'
                    '<li>Gemsbok in the Kalahari can go a long time without drinking water.</li>'
                    '<li>Fish have gills to breathe in water and fins to swim.</li>'
                    '<li>Monkeys have strong hands and tails for climbing trees.</li></ul>'
                    '<p>If a habitat is destroyed, for example when forests are cut down or rivers are polluted, '
                    'the plants and animals that live there may die out.</p>'
                ),
                'key_terms': [
                    ('habitat', 'the place where a plant or animal lives'),
                    ('shelter', 'a safe place to rest, sleep and hide'),
                    ('adapted', 'having features that help a living thing survive in its habitat'),
                ],
                'example': {
                    'title': 'Worked example: a pond habitat',
                    'html': (
                        '<p>Think about a pond. What does it provide?</p>'
                        '<ul><li><strong>Water</strong> for frogs, fish and water plants.</li>'
                        '<li><strong>Food:</strong> insects for frogs, water plants for snails.</li>'
                        '<li><strong>Shelter:</strong> reeds where birds build nests and fish hide.</li>'
                        '<li><strong>Breeding place:</strong> frogs lay their eggs in the water.</li></ul>'
                        '<p>A frog is adapted to the pond: webbed feet for swimming and moist skin.</p>'
                    ),
                },
                'video': {'id': '40B2IjLWfTQ',
                          'title': 'Habitats for Kids | Learn all about deserts, forests, grasslands, mountains, and more',
                          'channel': 'Learn Bright', 'minutes': 10},
                'worksheet': {
                    'instructions': 'Answer the questions. Use the notes to help you.',
                    'exercises': [
                        '1. What is a habitat?',
                        '2. Name four things a habitat must provide.',
                        '3. Name one large habitat and one small habitat.',
                        '4. How is a succulent plant adapted to living in a dry place?',
                        '5. How is a fish adapted to living in water? Give two features.',
                        '6. What might happen to animals if their forest habitat is cut down?',
                    ],
                },
                'quiz': [
                    ('mcq', 'A habitat is ...', ['a type of food', 'the place where a living thing lives', 'a kind of animal'], 1),
                    ('tf', 'A rotting log can be a habitat for small animals.', True),
                    ('mcq', 'Which feature helps a fish breathe in water?', ['Lungs', 'Feathers', 'Fur', 'Gills'], 3),
                    ('tf', 'Succulents store water in their thick leaves.', True),
                    ('tf', 'Destroying a habitat has no effect on the animals living there.', False),
                ],
                'homework': {
                    'title': 'Habitat fact card',
                    'instructions': 'Choose one South African animal and make a fact card about its habitat.',
                    'tasks': [
                        'Name the animal and draw or describe its habitat.',
                        'Explain how the habitat gives it food, water and shelter.',
                        'Describe one way the animal is adapted to its habitat.',
                    ],
                    'marks': 10,
                },
            },
            {
                'title': 'Living things need each other',
                'minutes': 45,
                'objectives': [
                    'Learners will explain what interdependence means.',
                    'Learners will describe ways animals depend on plants and plants depend on animals.',
                    'Learners will predict what could happen if one living thing disappears.',
                ],
                'notes': (
                    '<p>Plants and animals in a habitat <strong>depend on each other</strong>. This is called '
                    '<strong>interdependence</strong>.</p>'
                    '<p><strong>Animals need plants for:</strong></p>'
                    '<ul><li><strong>food</strong> - a cow eats grass, a monkey eats fruit;</li>'
                    '<li><strong>shelter</strong> - birds nest in trees, insects hide under leaves;</li>'
                    '<li><strong>oxygen</strong> - plants give off oxygen that animals breathe in.</li></ul>'
                    '<p><strong>Plants need animals for:</strong></p>'
                    '<ul><li><strong>pollination</strong> - bees, sunbirds and beetles carry pollen from '
                    'flower to flower so that seeds can form;</li>'
                    '<li><strong>seed dispersal</strong> - birds eat fruit and drop the seeds far away; seeds '
                    'with hooks stick to animal fur;</li>'
                    '<li><strong>nutrients</strong> - animal dung and dead animals rot and feed the soil.</li></ul>'
                    '<p>Animals also depend on other animals: a lion eats zebras, and oxpecker birds eat '
                    'ticks off buffaloes. If one living thing disappears, others are affected. If all the '
                    'bees disappeared, many plants could not make seeds, and animals that eat those fruits '
                    'would go hungry.</p>'
                ),
                'key_terms': [
                    ('interdependence', 'living things depending on each other to survive'),
                    ('pollination', 'moving pollen from one flower to another so seeds can form'),
                    ('seed dispersal', 'the spreading of seeds away from the parent plant'),
                ],
                'example': {
                    'title': 'Worked example: the bee and the flower',
                    'html': (
                        '<p>A bee visits an aloe flower to drink nectar (its food). Pollen sticks to its '
                        'hairy body. At the next aloe flower some pollen rubs off. Now the second flower is '
                        '<strong>pollinated</strong> and can make seeds.</p>'
                        '<p><strong>The bee gets:</strong> food (nectar). <strong>The aloe gets:</strong> '
                        'pollination. Both benefit - they are interdependent.</p>'
                    ),
                },
                'video': {'id': '4Qp_Um1bWsc',
                          'title': 'Inter Dependence Between Living Things | Science For Kids | Periwinkle',
                          'channel': 'Periwinkle', 'minutes': 6},
                'worksheet': {
                    'instructions': 'Answer the questions in full sentences.',
                    'exercises': [
                        '1. What does interdependence mean?',
                        '2. Give three ways animals depend on plants.',
                        '3. Give three ways plants depend on animals.',
                        '4. Explain how a bird that eats berries helps the berry bush.',
                        '5. What do oxpeckers get from buffaloes, and what do buffaloes get from oxpeckers?',
                        '6. Predict what could happen to flowering plants if there were no bees.',
                    ],
                },
                'quiz': [
                    ('mcq', 'Carrying pollen from flower to flower is called ...', ['dispersal', 'pollination', 'excretion'], 1),
                    ('tf', 'Animals depend on plants for the oxygen they breathe.', True),
                    ('mcq', 'Which is an example of seed dispersal by animals?',
                     ['A bee drinking nectar', 'A bird dropping seeds after eating fruit', 'A cow sleeping in the shade', 'A frog laying eggs'], 1),
                    ('tf', 'If one kind of animal disappears from a habitat, no other living things are affected.', False),
                ],
                'homework': {
                    'title': 'Who needs whom?',
                    'instructions': 'Draw a simple picture that shows interdependence in a garden or the veld.',
                    'tasks': [
                        'Draw at least two plants and two animals.',
                        'Draw arrows and label them to show three ways they depend on each other.',
                    ],
                    'marks': 10,
                },
            },
        ],
    },
    (6, 'NST'): {
        'topic': 'Photosynthesis',
        'caps': 'Life and Living: Photosynthesis - plants make their own food using sunlight, water and '
                'carbon dioxide; plants give off oxygen; plants as the source of all food',
        'summary': 'Learners investigate how green plants make their own food through photosynthesis, '
                   'what they need, what they produce and why all food chains start with plants.',
        'days': [
            {
                'title': 'Plants make their own food',
                'minutes': 50,
                'objectives': [
                    'Learners will explain that green plants make their own food.',
                    'Learners will name the things a plant needs for photosynthesis.',
                    'Learners will identify the leaf as the main food factory of a plant.',
                ],
                'notes': (
                    '<p>Animals and people must eat to get food. Green plants are different: they '
                    '<strong>make their own food</strong>. The process is called <strong>photosynthesis</strong>. '
                    '"Photo" means light and "synthesis" means putting together - plants use light to put '
                    'together food.</p>'
                    '<p>For photosynthesis a plant needs:</p>'
                    '<ul>'
                    '<li><strong>Sunlight</strong> - the energy that drives the process.</li>'
                    '<li><strong>Water</strong> - taken up from the soil by the roots and carried up the stem to the leaves.</li>'
                    '<li><strong>Carbon dioxide</strong> - a gas from the air that enters the leaf through tiny '
                    'openings called <strong>stomata</strong> (on the underside of the leaf).</li>'
                    '<li><strong>Chlorophyll</strong> - the green substance in leaves that traps the sunlight.</li>'
                    '</ul>'
                    '<p>The <strong>leaf</strong> is the plant\'s food factory. Leaves are flat and thin with '
                    'a large surface to catch as much light as possible. Plants that are kept in the dark '
                    'become pale and weak because they cannot make enough food.</p>'
                ),
                'key_terms': [
                    ('photosynthesis', 'the process in which green plants use sunlight to make food'),
                    ('chlorophyll', 'the green substance in leaves that traps light energy'),
                    ('carbon dioxide', 'a gas in the air that plants take in to make food'),
                    ('stomata', 'tiny openings in a leaf through which gases move in and out'),
                ],
                'example': {
                    'title': 'Investigation: light and no light',
                    'html': (
                        '<p>Take two similar seedlings in pots. Water both the same amount. Put one on a sunny '
                        'windowsill and one inside a dark cupboard for one week.</p>'
                        '<ul><li><strong>Question:</strong> Do plants need light to stay healthy?</li>'
                        '<li><strong>Fair test:</strong> only the light is changed; water, soil and pot size stay the same.</li>'
                        '<li><strong>Expected result:</strong> the plant in the dark turns pale/yellow and weak.</li>'
                        '<li><strong>Conclusion:</strong> plants need light to make food (photosynthesis).</li></ul>'
                    ),
                },
                'video': {'id': 'u46A0WKp2nk',
                          'title': 'How Plants Grow for Kids | Learn about photosynthesis and what plants need to grow strong',
                          'channel': 'Learn Bright', 'minutes': 10},
                'worksheet': {
                    'instructions': 'Answer the questions in full sentences.',
                    'exercises': [
                        '1. What is photosynthesis?',
                        '2. Name the four things a plant needs for photosynthesis.',
                        '3. How does water get from the soil to the leaves?',
                        '4. How does carbon dioxide get into the leaf?',
                        '5. What is the job of chlorophyll?',
                        '6. Why are leaves usually broad and flat?',
                        '7. In the investigation above, which variable was changed and which were kept the same?',
                    ],
                },
                'quiz': [
                    ('mcq', 'Which part of the plant is its main food factory?', ['Root', 'Leaf', 'Flower', 'Seed'], 1),
                    ('mcq', 'Which gas does a plant take in from the air to make food?', ['Oxygen', 'Nitrogen', 'Carbon dioxide'], 2),
                    ('tf', 'Chlorophyll is the green substance that traps sunlight.', True),
                    ('tf', 'Plants take in water mainly through their leaves.', False),
                ],
                'homework': {
                    'title': 'Start a light investigation',
                    'instructions': 'Set up a simple investigation at home and record it.',
                    'tasks': [
                        'Cover part of a leaf on a pot plant or garden plant with a strip of foil or paper (do not pick it).',
                        'Write down your question, what you did and what you predict will happen after 5 days.',
                    ],
                    'marks': 8,
                },
            },
            {
                'title': 'The photosynthesis word equation',
                'minutes': 50,
                'objectives': [
                    'Learners will write the word equation for photosynthesis.',
                    'Learners will identify the raw materials and products of photosynthesis.',
                    'Learners will explain that plants store extra food as starch.',
                ],
                'notes': (
                    '<p>Scientists summarise photosynthesis in a <strong>word equation</strong>:</p>'
                    '<p><strong>carbon dioxide + water</strong> --(sunlight, chlorophyll)--&gt; '
                    '<strong>glucose + oxygen</strong></p>'
                    '<ul>'
                    '<li>The things on the left are the <strong>raw materials</strong> (what goes in): carbon dioxide and water.</li>'
                    '<li>Sunlight and chlorophyll are written above the arrow because they are needed, but they are not used up as ingredients.</li>'
                    '<li>The things on the right are the <strong>products</strong> (what is made): '
                    '<strong>glucose</strong>, a kind of sugar (food), and <strong>oxygen</strong>.</li>'
                    '</ul>'
                    '<p>The plant uses some glucose straight away for energy to grow. Extra glucose is changed '
                    'into <strong>starch</strong> and stored in leaves, stems, roots, fruits and seeds. '
                    'Potatoes, sweet potatoes and maize are full of stored starch.</p>'
                    '<p>Oxygen is released into the air through the stomata. This is the oxygen that animals '
                    'and people breathe. We can test a leaf for starch with <strong>iodine solution</strong>: '
                    'iodine turns <strong>blue-black</strong> where starch is present.</p>'
                ),
                'key_terms': [
                    ('raw materials', 'the substances a process starts with'),
                    ('products', 'the substances a process makes'),
                    ('glucose', 'a simple sugar made by plants in photosynthesis'),
                    ('starch', 'the form in which plants store extra food'),
                ],
                'example': {
                    'title': 'Worked example: reading the equation',
                    'html': (
                        '<p><strong>Question:</strong> A plant is kept in a sealed jar in the sun. What '
                        'happens to the amounts of carbon dioxide and oxygen in the jar?</p>'
                        '<p><strong>Answer:</strong> From the equation, carbon dioxide is a raw material, so it '
                        'is used up and its amount <strong>decreases</strong>. Oxygen is a product, so its amount '
                        '<strong>increases</strong>.</p>'
                        '<p><strong>Demonstration (teacher only):</strong> a leaf boiled in alcohol to remove '
                        'chlorophyll and then dropped with iodine turns blue-black - it contains starch.</p>'
                    ),
                },
                'video': {'id': 'E22APTvfwyE', 'title': 'What is Photosynthesis?',
                          'channel': 'Next Generation Science', 'minutes': 4},
                'worksheet': {
                    'instructions': 'Use the word equation to answer the questions.',
                    'exercises': [
                        '1. Write the word equation for photosynthesis.',
                        '2. Name the two raw materials of photosynthesis.',
                        '3. Name the two products of photosynthesis.',
                        '4. Why are sunlight and chlorophyll written above the arrow?',
                        '5. In what form do plants store extra food?',
                        '6. Name two plant foods that contain a lot of starch.',
                        '7. What colour does iodine solution turn when starch is present?',
                    ],
                },
                'quiz': [
                    ('mcq', 'Which are the products of photosynthesis?',
                     ['Water and carbon dioxide', 'Glucose and oxygen', 'Oxygen and water', 'Starch and soil'], 1),
                    ('tf', 'Plants store extra glucose as starch.', True),
                    ('mcq', 'Iodine solution turns ... when starch is present.', ['red', 'blue-black', 'white'], 1),
                    ('tf', 'Oxygen is a raw material of photosynthesis.', False),
                    ('mcq', 'Which food is a store of plant starch?', ['Egg', 'Potato', 'Milk', 'Fish'], 1),
                ],
                'homework': {
                    'title': 'Equation and starch foods',
                    'instructions': 'Show what you have learnt about the word equation.',
                    'tasks': [
                        'Write the word equation and label the raw materials and the products.',
                        'Look in your kitchen and list 4 foods that come from plant parts that store starch.',
                        'Check your covered leaf from Day 1 and note any change in colour.',
                    ],
                    'marks': 10,
                },
            },
            {
                'title': 'Plants: the start of all food',
                'minutes': 50,
                'objectives': [
                    'Learners will explain why plants are called producers.',
                    'Learners will draw a simple food chain that starts with a plant.',
                    'Learners will explain why photosynthesis is important for all life.',
                ],
                'notes': (
                    '<p>Because plants make their own food, they are called <strong>producers</strong>. '
                    'Animals cannot make food, so they must eat plants or other animals. Animals are '
                    'called <strong>consumers</strong>.</p>'
                    '<p>All the food we eat can be traced back to plants:</p>'
                    '<ul><li>Bread comes from wheat (a plant).</li>'
                    '<li>Milk comes from a cow, and the cow ate grass (a plant).</li>'
                    '<li>Chicken meat comes from chickens that ate maize (a plant).</li></ul>'
                    '<p>A <strong>food chain</strong> shows who eats whom. The arrow means "is eaten by" and '
                    'points to the eater: <em>grass -&gt; grasshopper -&gt; bird -&gt; snake</em>. Every food '
                    'chain starts with a producer.</p>'
                    '<p>Photosynthesis is important for all life on Earth because it:</p>'
                    '<ol><li>makes the food that all other living things depend on,</li>'
                    '<li>releases the <strong>oxygen</strong> animals and people breathe,</li>'
                    '<li>removes carbon dioxide from the air.</li></ol>'
                    '<p>That is why protecting forests, grasslands and even ocean algae matters to us all.</p>'
                ),
                'key_terms': [
                    ('producer', 'a living thing that makes its own food (green plants)'),
                    ('consumer', 'a living thing that eats other living things for food'),
                    ('food chain', 'a diagram showing how food energy passes from one living thing to another'),
                ],
                'example': {
                    'title': 'Worked example: tracing a meal back to plants',
                    'html': (
                        '<p><strong>Meal:</strong> pap, chicken and spinach.</p>'
                        '<ul><li>Pap - made from maize meal, from the maize plant (producer).</li>'
                        '<li>Chicken - the chicken ate maize and seeds: maize -&gt; chicken -&gt; person.</li>'
                        '<li>Spinach - a leafy plant (producer).</li></ul>'
                        '<p><strong>Conclusion:</strong> every part of the meal depends on photosynthesis.</p>'
                    ),
                },
                'video': {'id': 'UPBMG5EYydo', 'title': 'Photosynthesis | Educational Video for Kids',
                          'channel': 'Happy Learning English', 'minutes': 4},
                'worksheet': {
                    'instructions': 'Answer the questions. Use "->" for the arrows in food chains.',
                    'exercises': [
                        '1. Why are green plants called producers?',
                        '2. What is a consumer? Give two examples.',
                        '3. Put in order to make a food chain: lion, grass, zebra.',
                        '4. Write a food chain with four living things that starts with a plant.',
                        '5. Trace a glass of milk back to a plant.',
                        '6. Give three reasons why photosynthesis is important for life on Earth.',
                    ],
                },
                'quiz': [
                    ('mcq', 'Every food chain starts with a ...', ['consumer', 'producer', 'predator'], 1),
                    ('mcq', 'In the food chain grass -> cow -> person, the cow is a ...',
                     ['producer', 'plant', 'consumer', 'decomposer'], 2),
                    ('tf', 'Photosynthesis releases the oxygen that animals breathe.', True),
                    ('tf', 'Animals can make their own food from sunlight.', False),
                ],
                'homework': {
                    'title': 'My food comes from plants',
                    'instructions': 'Think about the food you ate today.',
                    'tasks': [
                        'Choose one meal you ate and trace every food in it back to a plant.',
                        'Draw one food chain from your meal with labels: producer and consumer.',
                        'Write a short paragraph: "Why we cannot live without plants".',
                    ],
                    'marks': 12,
                },
            },
        ],
    },
    # -------------------------------------------------------------- SOC-SCI
    (4, 'SOC-SCI'): {
        'topic': 'Geography: Places where people live',
        'caps': 'Geography Term 1: Places where people live - people and places; settlements; '
                'rural and urban areas; why people choose to live where they do',
        'summary': 'Learners explore what a settlement is, compare rural and urban places and work out '
                   'why people settle in certain places.',
        'days': [
            {
                'title': 'What is a settlement?',
                'minutes': 45,
                'objectives': [
                    'I can explain what a settlement is.',
                    'I can name different kinds of settlements, from a farm to a city.',
                    'I can describe the place where I live.',
                ],
                'notes': (
                    '<p>A <strong>settlement</strong> is a place where people live. It can be very small '
                    'or very big. Settlements are made up of homes and the buildings and places people use, '
                    'such as shops, schools, clinics, roads and places of worship.</p>'
                    '<p>From smallest to biggest, settlements include:</p>'
                    '<ul>'
                    '<li><strong>a farm</strong> - one or a few homes where people grow crops or keep animals,</li>'
                    '<li><strong>a village</strong> - a small group of homes, maybe a school and a small shop,</li>'
                    '<li><strong>a town</strong> - many homes, shops, a few schools, a clinic and a police station,</li>'
                    '<li><strong>a city</strong> - a very large settlement with many people, tall buildings, '
                    'factories, hospitals and universities, such as Johannesburg, Cape Town and Durban.</li>'
                    '</ul>'
                    '<p>Every settlement has a <strong>name</strong> and an <strong>address</strong> system. '
                    'Your address tells people where you live: house number, street, suburb or village, '
                    'town or city, and province.</p>'
                    '<p>In South Africa people live in many kinds of homes: brick houses, flats, '
                    'traditional round houses, farmhouses and informal homes.</p>'
                ),
                'key_terms': [
                    ('settlement', 'a place where people live'),
                    ('village', 'a small settlement, usually in the countryside'),
                    ('city', 'a very large settlement with many people and services'),
                    ('province', 'one of the nine parts South Africa is divided into'),
                ],
                'example': {
                    'title': 'Class activity: settlement ladder',
                    'html': (
                        '<p>Draw a ladder with four steps. On the bottom step write <strong>farm</strong>, then '
                        '<strong>village</strong>, <strong>town</strong> and <strong>city</strong> at the top.</p>'
                        '<p>Next to each step, write one thing you would find there. For example: '
                        'farm - cattle kraal; village - small shop; town - clinic; city - airport.</p>'
                        '<p>Discuss: where on the ladder is the place where you live?</p>'
                    ),
                },
                'video': {'id': 'sClVS0WazSI', 'title': 'EOS Gr4 Revision Geography: What is a settlement?',
                          'channel': 'Edgemead Primary School', 'minutes': 5},
                'worksheet': {
                    'instructions': 'Answer the questions in full sentences.',
                    'exercises': [
                        '1. What is a settlement?',
                        '2. Put these in order from smallest to biggest: town, farm, city, village.',
                        '3. Name two things you would find in a town but maybe not on a farm.',
                        '4. Name two big cities in South Africa.',
                        '5. Write the parts of an address (do not use your real house number).',
                        '6. Describe the kind of settlement you live in.',
                    ],
                },
                'quiz': [
                    ('mcq', 'A place where people live is called a ...', ['settlement', 'continent', 'river', 'mountain'], 0),
                    ('mcq', 'Which is the biggest settlement?', ['Farm', 'Village', 'Town', 'City'], 3),
                    ('tf', 'Johannesburg is a city.', True),
                    ('tf', 'A village usually has more people than a city.', False),
                ],
                'homework': {
                    'title': 'Where I live',
                    'instructions': 'Talk to an adult at home about your settlement.',
                    'tasks': [
                        'Write the name of your settlement, town or city, and province.',
                        'Draw a picture of your home and two buildings near it that people use.',
                        'Write two sentences about what you like about where you live.',
                    ],
                    'marks': 10,
                },
            },
            {
                'title': 'Rural and urban areas',
                'minutes': 45,
                'objectives': [
                    'I can explain the difference between rural and urban areas.',
                    'I can compare the work people do in rural and urban areas.',
                    'I can sort pictures or descriptions into rural or urban.',
                ],
                'notes': (
                    '<p>Settlements can be found in <strong>rural</strong> areas or <strong>urban</strong> areas.</p>'
                    '<p><strong>Rural areas</strong> are in the countryside. Farms and villages are rural. '
                    'There is lots of open land and fewer people. Homes are spread far apart. Many people '
                    'work on the land: farming crops such as maize, keeping cattle, sheep or goats, or '
                    'working in forests or mines. People may travel far to get to a hospital or big shop.</p>'
                    '<p><strong>Urban areas</strong> are towns and cities. Many people live close together. '
                    'There are tall buildings, busy roads, traffic lights and lots of shops. People work in '
                    'offices, factories, shops, hospitals, schools and banks. Services like water, electricity, '
                    'buses and taxis are usually close by.</p>'
                    '<p>Both areas need each other. Rural areas grow the food that city people eat. Urban '
                    'areas make goods, such as clothes and tools, and provide services such as hospitals and '
                    'universities that rural people use.</p>'
                    '<p>Some people live in <em>suburbs</em> - quieter areas of homes on the edge of a town or city.</p>'
                ),
                'key_terms': [
                    ('rural', 'the countryside: farms and villages with few people'),
                    ('urban', 'towns and cities where many people live close together'),
                    ('services', 'help provided to people, e.g. water, clinics, schools, transport'),
                    ('suburb', 'a mostly residential area on the edge of a town or city'),
                ],
                'example': {
                    'title': 'Guided activity: rural or urban?',
                    'html': (
                        '<p>Read each clue and say R (rural) or U (urban):</p>'
                        '<ol><li>A farmer milks cows at sunrise. <em>(R)</em></li>'
                        '<li>Hundreds of cars wait at traffic lights. <em>(U)</em></li>'
                        '<li>A girl walks 3 km past fields to school. <em>(R)</em></li>'
                        '<li>People go up in a lift to their office on the 20th floor. <em>(U)</em></li></ol>'
                        '<p>Then fill in a two-column table comparing homes, jobs and transport in each area.</p>'
                    ),
                },
                'video': {'id': 'YRxNQPmj1-8', 'title': 'Urban, Suburban and Rural Areas for Kids',
                          'channel': 'Homeschool Pop', 'minutes': 6},
                'worksheet': {
                    'instructions': 'Write R for rural or U for urban, then answer the questions.',
                    'exercises': [
                        '1. A shopping mall with a cinema ____',
                        '2. A goat herder in the hills ____',
                        '3. A factory making cars ____',
                        '4. A maize field ____',
                        '5. Name two jobs people do in rural areas and two jobs in urban areas.',
                        '6. Give one way rural areas help urban areas and one way urban areas help rural areas.',
                        '7. Do you live in a rural or an urban area? Give a reason.',
                    ],
                },
                'quiz': [
                    ('mcq', 'Farms and villages are found in ... areas.', ['urban', 'rural', 'city'], 1),
                    ('tf', 'Urban areas usually have more people living close together than rural areas.', True),
                    ('mcq', 'Which job is most likely in a rural area?', ['Bank teller', 'Office worker', 'Sheep farmer', 'Traffic officer'], 2),
                    ('tf', 'Rural and urban areas do not depend on each other at all.', False),
                ],
                'homework': {
                    'title': 'Two places, two lives',
                    'instructions': 'Compare life in a rural area and an urban area.',
                    'tasks': [
                        'Draw two boxes. In one, draw a rural scene; in the other, an urban scene.',
                        'Write three differences between the two places under your drawings.',
                    ],
                    'marks': 10,
                },
            },
            {
                'title': 'Why people live where they do',
                'minutes': 45,
                'objectives': [
                    'I can name the things people need when choosing a place to live.',
                    'I can explain why many settlements grow near rivers, good soil or transport routes.',
                    'I can choose the best place for a new settlement and give reasons.',
                ],
                'notes': (
                    '<p>Long ago, and still today, people choose where to live by thinking about what they '
                    '<strong>need</strong>:</p>'
                    '<ul>'
                    '<li><strong>Water</strong> - for drinking, cooking, washing and farming. Many settlements '
                    'grew up next to rivers or springs.</li>'
                    '<li><strong>Good soil and flat land</strong> - for growing crops and building homes.</li>'
                    '<li><strong>Safety</strong> - away from floods, on higher ground, or protected by hills.</li>'
                    '<li><strong>Building materials and fuel</strong> - wood, stone, clay and grass nearby.</li>'
                    '<li><strong>Work</strong> - people move to places with jobs, for example Johannesburg grew '
                    'quickly after gold was found there in 1886.</li>'
                    '<li><strong>Transport</strong> - settlements grow near roads, railways and harbours, '
                    'such as Durban and Cape Town, which are port cities.</li>'
                    '</ul>'
                    '<p>Today people also want <strong>services</strong> close by: schools, clinics, shops, '
                    'electricity and transport. That is one reason why many people move from rural to urban areas.</p>'
                    '<p>Some places are poor choices for settlements: very steep slopes, land that floods, '
                    'or places with no water.</p>'
                ),
                'key_terms': [
                    ('site', 'the actual piece of land on which a settlement is built'),
                    ('natural resources', 'useful things from nature, e.g. water, soil, wood'),
                    ('harbour', 'a sheltered place on the coast where ships can dock'),
                ],
                'example': {
                    'title': 'Guided activity: choose a site',
                    'html': (
                        '<p>Imagine a map with three possible sites:</p>'
                        '<ul><li><strong>Site A:</strong> on a steep, rocky mountain far from water.</li>'
                        '<li><strong>Site B:</strong> on flat land next to a river, with trees and good soil, '
                        'on slightly higher ground.</li>'
                        '<li><strong>Site C:</strong> in a low marsh that floods every summer.</li></ul>'
                        '<p><strong>Best choice:</strong> Site B - it has water, good soil, building wood and is '
                        'safe from floods. Site A has no water and is hard to build on; Site C floods.</p>'
                    ),
                },
                'video': {'id': '6uK0t6HH7QA', 'title': 'Settlements and What People Need',
                          'channel': 'i-Simplify Study', 'minutes': 5},
                'worksheet': {
                    'instructions': 'Answer the questions in full sentences.',
                    'exercises': [
                        '1. Name four things people need when choosing a place to live.',
                        '2. Why did many settlements grow next to rivers?',
                        '3. Why did Johannesburg grow so quickly after 1886?',
                        '4. Why are Durban and Cape Town good places for ports?',
                        '5. Give two reasons why a marsh that floods is a bad place to build.',
                        '6. Why do many people move from rural areas to cities today?',
                    ],
                },
                'quiz': [
                    ('mcq', 'Why did many early settlements grow next to rivers?',
                     ['Rivers are noisy', 'People needed water', 'Rivers keep animals away'], 1),
                    ('tf', 'Land that floods every year is a good site for a settlement.', False),
                    ('mcq', 'Johannesburg grew quickly after ... was found there.', ['coal', 'diamonds', 'oil', 'gold'], 3),
                    ('tf', 'People often move to places where they can find work.', True),
                ],
                'homework': {
                    'title': 'Design a settlement',
                    'instructions': 'Plan your own small settlement.',
                    'tasks': [
                        'Draw a simple map of a good site for a new village. Show water, farmland, homes and a road.',
                        'Write three reasons why you chose this site.',
                    ],
                    'marks': 10,
                },
            },
        ],
    },
    (5, 'SOC-SCI'): {
        'topic': 'Geography: Map skills',
        'caps': 'Geography Term 1: Map skills - symbols and keys; side view and plan view; '
                'compass directions (8 points); alpha-numeric grid references',
        'summary': 'Learners read map symbols and keys, use the eight compass directions and find places '
                   'on a map with alpha-numeric grid references.',
        'days': [
            {
                'title': 'Plan view, symbols and the map key',
                'minutes': 45,
                'objectives': [
                    'Learners will explain the difference between side view and plan view.',
                    'Learners will use symbols and a key to read a map.',
                    'Learners will name the features every good map should have.',
                ],
                'notes': (
                    '<p>A <strong>map</strong> is a drawing of a place as seen from directly above. This '
                    'bird\'s-eye view is called a <strong>plan view</strong>. A photo of a house from the street '
                    'is a <strong>side view</strong>: you see the walls, door and windows. In plan view you '
                    'only see the roof.</p>'
                    '<p>Maps cannot show every detail, so they use <strong>symbols</strong>: small drawings, '
                    'lines, letters or colours that stand for real things. For example:</p>'
                    '<ul><li>a blue line for a river,</li><li>a cross for a church,</li>'
                    '<li>a red or black line for a road,</li><li>green for forests or parks.</li></ul>'
                    '<p>The <strong>key</strong> (or legend) is a box on the map that explains what every '
                    'symbol means. Always read the key first!</p>'
                    '<p>A good map has:</p>'
                    '<ol><li>a <strong>title</strong> (what the map shows),</li><li>a <strong>key</strong>,</li>'
                    '<li>a <strong>north arrow</strong> or compass rose,</li>'
                    '<li>a <strong>scale</strong> (how distance on the map compares to real distance),</li>'
                    '<li>often a <strong>grid</strong> to help find places.</li></ol>'
                ),
                'key_terms': [
                    ('plan view', 'a view from directly above (bird\'s-eye view)'),
                    ('side view', 'a view from the side, as you see things standing in front of them'),
                    ('symbol', 'a small drawing, line or colour that stands for a real thing on a map'),
                    ('key', 'the part of a map that explains what the symbols mean'),
                ],
                'example': {
                    'title': 'Class activity: classroom map',
                    'html': (
                        '<p>Draw a plan view of your classroom.</p>'
                        '<ol><li>Draw the outline of the room as a rectangle.</li>'
                        '<li>Use symbols: a small square for each desk, a long rectangle for the board, '
                        'a gap in the wall for the door, a double line for windows.</li>'
                        '<li>Draw a key that explains each symbol.</li>'
                        '<li>Add a title: "Plan of our classroom".</li></ol>'
                    ),
                },
                'video': {'id': 'dp8VOG8Cgag', 'title': 'Learn About Maps - Symbols, Map Key, Compass Rose',
                          'channel': 'Vids4Kids.tv', 'minutes': 4},
                'worksheet': {
                    'instructions': 'Answer the questions. Draw where you are asked to.',
                    'exercises': [
                        '1. What is the difference between a side view and a plan view?',
                        '2. Draw a cup in side view and in plan view.',
                        '3. Why do maps use symbols instead of pictures of everything?',
                        '4. What is a map key and why is it important?',
                        '5. Draw symbols for: a school, a river, a hospital and a road.',
                        '6. List four features that every good map should have.',
                    ],
                },
                'quiz': [
                    ('mcq', 'A view from directly above is called a ...', ['side view', 'plan view', 'front view'], 1),
                    ('mcq', 'The part of a map that explains the symbols is the ...', ['title', 'scale', 'key', 'grid'], 2),
                    ('tf', 'Rivers are usually shown with a blue line on maps.', True),
                    ('tf', 'A map does not need a title.', False),
                ],
                'homework': {
                    'title': 'My bedroom from above',
                    'instructions': 'Draw a plan view of your bedroom or the room where you sleep.',
                    'tasks': [
                        'Draw the room from above using at least 5 symbols.',
                        'Add a key and a title.',
                    ],
                    'marks': 10,
                },
            },
            {
                'title': 'Compass directions',
                'minutes': 45,
                'objectives': [
                    'Learners will name and draw the 8 points of the compass.',
                    'Learners will use compass directions to describe where places are on a map.',
                    'Learners will give simple directions from one place to another.',
                ],
                'notes': (
                    '<p>We use <strong>compass directions</strong> to describe where places are. A '
                    '<strong>compass rose</strong> on a map shows the directions.</p>'
                    '<p>The four <strong>main (cardinal) directions</strong> are <strong>North (N), East (E), '
                    'South (S) and West (W)</strong>. Going clockwise from North, a helpful rhyme is '
                    '"<em>Never Eat Soggy Weetbix</em>".</p>'
                    '<p>Between them are four <strong>in-between (intermediate) directions</strong>:</p>'
                    '<ul><li><strong>North-East (NE)</strong> between N and E,</li>'
                    '<li><strong>South-East (SE)</strong> between S and E,</li>'
                    '<li><strong>South-West (SW)</strong> between S and W,</li>'
                    '<li><strong>North-West (NW)</strong> between N and W.</li></ul>'
                    '<p>Notice that North or South always comes first in the name.</p>'
                    '<p>On most maps, North is at the top. The sun rises in the <strong>east</strong> and sets '
                    'in the <strong>west</strong>, which can help you find directions outside.</p>'
                    '<p>Examples from a map of South Africa: Limpopo is in the north; the Western Cape is in '
                    'the south-west; KwaZulu-Natal is in the east. Johannesburg is north-east of Kimberley.</p>'
                ),
                'key_terms': [
                    ('compass rose', 'a symbol on a map showing the directions'),
                    ('cardinal directions', 'the four main directions: N, E, S, W'),
                    ('intermediate directions', 'the in-between directions: NE, SE, SW, NW'),
                ],
                'example': {
                    'title': 'Worked example: using directions',
                    'html': (
                        '<p>On a map of a town, the school is in the middle. The park is above it, the shop '
                        'is to the right, the clinic is below and to the left, and the church is above and to the right.</p>'
                        '<ul><li>The park is <strong>north</strong> of the school.</li>'
                        '<li>The shop is <strong>east</strong> of the school.</li>'
                        '<li>The clinic is <strong>south-west</strong> of the school.</li>'
                        '<li>The church is <strong>north-east</strong> of the school.</li></ul>'
                        '<p>Then: the school is <strong>north-east</strong> of the clinic (the opposite direction).</p>'
                    ),
                },
                'video': {'id': 'FdSr0SzGZ2Y', 'title': 'Maps Skills: a Compass Rose',
                          'channel': 'Teaching Independent Learners', 'minutes': 4},
                'worksheet': {
                    'instructions': 'Draw a compass rose with all 8 points, then answer the questions.',
                    'exercises': [
                        '1. Draw and label a compass rose with N, NE, E, SE, S, SW, W and NW.',
                        '2. Which direction is opposite North-East?',
                        '3. Which direction is between South and West?',
                        '4. In which direction does the sun rise?',
                        '5. On a map of South Africa, in which part of the country is Limpopo?',
                        '6. If you face North and turn to your right, which direction do you face?',
                        '7. Write directions from your home to a nearby shop using at least two compass directions.',
                    ],
                },
                'quiz': [
                    ('mcq', 'Which direction is between North and West?', ['North-East', 'South-West', 'North-West', 'South-East'], 2),
                    ('mcq', 'What is the opposite of South-East?', ['North-West', 'North-East', 'South-West'], 0),
                    ('tf', 'The sun rises in the west.', False),
                    ('tf', 'On most maps, North is at the top.', True),
                ],
                'homework': {
                    'title': 'Directions at home',
                    'instructions': 'Find the directions around your home (the sun rises in the east).',
                    'tasks': [
                        'Stand outside in the morning and find East using the sun. Then work out N, S and W.',
                        'Write which direction your front door faces.',
                        'Name one thing (a tree, building or road) to the north, east, south and west of your home.',
                    ],
                    'marks': 10,
                },
            },
            {
                'title': 'Finding places with grid references',
                'minutes': 45,
                'objectives': [
                    'Learners will explain what a grid is and why maps use one.',
                    'Learners will give the alpha-numeric grid reference of a place.',
                    'Learners will find a place on a map from its grid reference.',
                ],
                'notes': (
                    '<p>Many maps have a <strong>grid</strong>: lines that divide the map into squares, like a '
                    'chessboard. Grids help us find places quickly and tell other people exactly where something is.</p>'
                    '<p>An <strong>alpha-numeric grid</strong> uses <strong>letters</strong> (alpha) along one '
                    'side and <strong>numbers</strong> (numeric) along the other. Each square has its own '
                    '<strong>grid reference</strong>, such as <strong>B3</strong>.</p>'
                    '<p>How to give a grid reference:</p>'
                    '<ol><li>Find the place on the map.</li>'
                    '<li>Move your finger straight <strong>across</strong> (or down) to read the '
                    '<strong>letter</strong>.</li>'
                    '<li>Then move straight <strong>up or down</strong> to the side to read the '
                    '<strong>number</strong>.</li>'
                    '<li>Write the letter first, then the number: e.g. <strong>C2</strong>.</li></ol>'
                    '<p>Remember: on our maps the letters run along the bottom (columns) and the numbers up the '
                    'side (rows). Always write the <strong>letter before the number</strong>. Atlases use the '
                    'same idea: the index tells you the page and the grid square of each town.</p>'
                ),
                'key_terms': [
                    ('grid', 'lines that divide a map into squares'),
                    ('alpha-numeric', 'using both letters and numbers'),
                    ('grid reference', 'the letter and number that name one square of a grid, e.g. B3'),
                    ('atlas', 'a book of maps'),
                ],
                'example': {
                    'title': 'Worked example: a town grid',
                    'html': (
                        '<p>A map has columns A, B, C, D along the bottom and rows 1, 2, 3, 4 up the side.</p>'
                        '<ul><li>The library is in column B, row 3: grid reference <strong>B3</strong>.</li>'
                        '<li>The station is in column D, row 1: <strong>D1</strong>.</li>'
                        '<li>What is in A4? Go to column A, then up to row 4 - the dam.</li></ul>'
                        '<p><strong>Common mistake:</strong> writing "3B". The letter always comes first.</p>'
                    ),
                },
                'video': {'id': 'NCbaRMIlu6E', 'title': '[GRADE 4] Alpha-numeric grid references',
                          'channel': 'Maski TV Juniors', 'minutes': 5},
                'worksheet': {
                    'instructions': 'Draw a 4 x 4 grid. Label the columns A-D along the bottom and the rows 1-4 up the side. Then do the tasks.',
                    'exercises': [
                        '1. Draw a house symbol in B2 and a tree symbol in D4.',
                        '2. Draw a river that flows through A1, B1, C1 and D1.',
                        '3. Draw a school in C3. What is its grid reference?',
                        '4. Draw a clinic in A3. Which direction is the clinic from the school?',
                        '5. Why must the letter always be written before the number?',
                        '6. How does a grid help someone find a place quickly?',
                    ],
                },
                'quiz': [
                    ('mcq', 'Which is a correctly written alpha-numeric grid reference?', ['4C', 'C4', '44', 'CC'], 1),
                    ('tf', 'A grid divides a map into squares.', True),
                    ('mcq', '"Alpha-numeric" means using ...', ['only numbers', 'only letters', 'letters and numbers'], 2),
                    ('tf', 'An atlas index can tell you the grid square where a town is found.', True),
                ],
                'homework': {
                    'title': 'Treasure map',
                    'instructions': 'Make a treasure map with an alpha-numeric grid.',
                    'tasks': [
                        'Draw a 5 x 5 grid (A-E and 1-5) and add at least 6 symbols with a key.',
                        'Add a compass rose.',
                        'Write the grid reference of each symbol and hide a treasure X - write its grid reference on the back.',
                    ],
                    'marks': 15,
                },
            },
        ],
    },
    (6, 'SOC-SCI'): {
        'topic': 'Geography: Map skills - latitude and longitude',
        'caps': 'Geography Term 1: Map skills - lines of latitude and longitude; Equator, Prime '
                'Meridian, tropics and hemispheres; degrees; locating places using a global address',
        'summary': 'Learners use the globe and atlas to understand hemispheres, lines of latitude and '
                   'longitude, and give the global address of places in South Africa and the world.',
        'days': [
            {
                'title': 'The globe, the Equator and hemispheres',
                'minutes': 50,
                'objectives': [
                    'Learners will explain the difference between a globe and a world map.',
                    'Learners will identify the Equator and the Prime Meridian.',
                    'Learners will name the four hemispheres and say in which ones South Africa lies.',
                ],
                'notes': (
                    '<p>A <strong>globe</strong> is a round model of the Earth. It shows the true shapes and '
                    'sizes of continents and oceans. A <strong>world map</strong> is flat, so some shapes and '
                    'sizes are stretched, but it is easier to carry and use.</p>'
                    '<p>To help us find places, mapmakers draw imaginary lines on the Earth.</p>'
                    '<ul>'
                    '<li>The <strong>Equator</strong> (0°) is an imaginary line around the middle of the Earth, '
                    'halfway between the North Pole and the South Pole. It divides the Earth into the '
                    '<strong>Northern Hemisphere</strong> and the <strong>Southern Hemisphere</strong>.</li>'
                    '<li>The <strong>Prime Meridian</strong> (0°) runs from the North Pole to the South Pole '
                    'through Greenwich in London, England. It divides the Earth into the '
                    '<strong>Eastern Hemisphere</strong> and the <strong>Western Hemisphere</strong>.</li>'
                    '</ul>'
                    '<p>"Hemi" means half, so a hemisphere is half of the Earth. South Africa lies south of '
                    'the Equator and east of the Prime Meridian, so it is in the <strong>Southern</strong> and '
                    '<strong>Eastern</strong> Hemispheres.</p>'
                    '<p>Other important lines are the <strong>Tropic of Cancer</strong> (about 23.5° N), the '
                    '<strong>Tropic of Capricorn</strong> (about 23.5° S), which passes through Limpopo province, '
                    'and the Arctic and Antarctic Circles.</p>'
                ),
                'key_terms': [
                    ('globe', 'a round model of the Earth'),
                    ('Equator', 'the imaginary line of 0° latitude around the middle of the Earth'),
                    ('Prime Meridian', 'the line of 0° longitude through Greenwich, London'),
                    ('hemisphere', 'half of the Earth'),
                ],
                'example': {
                    'title': 'Class activity: orange globe',
                    'html': (
                        '<p>Use an orange (or a ball) as a model of the Earth.</p>'
                        '<ol><li>Mark the top as the North Pole and the bottom as the South Pole.</li>'
                        '<li>Draw a line around the middle with a koki: the Equator.</li>'
                        '<li>Draw a line from pole to pole: the Prime Meridian.</li>'
                        '<li>Count the four parts - the hemispheres. Put a dot where South Africa would be '
                        '(below the Equator, just to the right of the Prime Meridian).</li></ol>'
                    ),
                },
                'video': {'id': 'T3YxzaZwHF0',
                          'title': '🌍 THE EQUATOR and the HEMISPHERES | Educational Videos for Children | @HappyLearningENG',
                          'channel': 'Happy Learning English', 'minutes': 4},
                'worksheet': {
                    'instructions': 'Use an atlas or the notes to answer the questions.',
                    'exercises': [
                        '1. Give one advantage of a globe and one advantage of a flat world map.',
                        '2. What is the Equator and what is its value in degrees?',
                        '3. Through which city does the Prime Meridian pass?',
                        '4. Name the four hemispheres.',
                        '5. In which two hemispheres is South Africa?',
                        '6. Which tropic passes through Limpopo province?',
                        '7. Name one continent that is mostly in the Northern Hemisphere.',
                    ],
                },
                'quiz': [
                    ('mcq', 'The Equator divides the Earth into the ...',
                     ['Eastern and Western Hemispheres', 'Northern and Southern Hemispheres', 'Arctic and Antarctic'], 1),
                    ('mcq', 'In which hemispheres is South Africa?',
                     ['Northern and Western', 'Southern and Western', 'Southern and Eastern', 'Northern and Eastern'], 2),
                    ('tf', 'The Prime Meridian passes through Greenwich in London.', True),
                    ('tf', 'The Tropic of Cancer passes through South Africa.', False),
                ],
                'homework': {
                    'title': 'Label the world',
                    'instructions': 'Draw a simple circle to represent the Earth.',
                    'tasks': [
                        'Draw and label the Equator, the Prime Meridian, the North Pole and the South Pole.',
                        'Label the four hemispheres.',
                        'Mark roughly where South Africa is and write which hemispheres it is in.',
                    ],
                    'marks': 10,
                },
            },
            {
                'title': 'Lines of latitude and longitude',
                'minutes': 50,
                'objectives': [
                    'Learners will describe lines of latitude and lines of longitude.',
                    'Learners will explain how latitude and longitude are measured in degrees.',
                    'Learners will read the latitude and longitude lines on an atlas map.',
                ],
                'notes': (
                    '<p><strong>Lines of latitude</strong> run <strong>east-west</strong> around the Earth, '
                    'parallel to the Equator. They are also called <strong>parallels</strong>. They measure '
                    'how far <strong>north or south</strong> of the Equator a place is. The Equator is 0°; the '
                    'North Pole is 90° N and the South Pole is 90° S.</p>'
                    '<p><strong>Lines of longitude</strong> run <strong>north-south</strong> from pole to pole. '
                    'They are also called <strong>meridians</strong>. They measure how far <strong>east or '
                    'west</strong> of the Prime Meridian a place is. The Prime Meridian is 0°; longitude goes up '
                    'to 180° E and 180° W.</p>'
                    '<p>Both are measured in <strong>degrees (°)</strong> because the Earth is round, like a circle.</p>'
                    '<p>Tips to remember:</p>'
                    '<ul><li><strong>Lat</strong>itude lines lie <strong>flat</strong> like the rungs of a ladder.</li>'
                    '<li><strong>Long</strong>itude lines are <strong>long</strong> - they all meet at the poles.</li>'
                    '<li>Latitude always has N or S; longitude always has E or W.</li></ul>'
                    '<p>All lines of latitude are parallel and never meet. Lines of longitude are furthest apart '
                    'at the Equator and come together at the poles.</p>'
                ),
                'key_terms': [
                    ('latitude', 'distance north or south of the Equator, in degrees'),
                    ('longitude', 'distance east or west of the Prime Meridian, in degrees'),
                    ('parallel', 'another name for a line of latitude'),
                    ('meridian', 'another name for a line of longitude'),
                ],
                'example': {
                    'title': 'Worked example: reading the lines',
                    'html': (
                        '<p>On an atlas map of Africa:</p>'
                        '<ul><li>Find the line labelled 30° S. It runs across South Africa near Durban. '
                        'Because it is <strong>S</strong>, it is a line of latitude south of the Equator.</li>'
                        '<li>Find the line labelled 20° E. It runs from top to bottom near Cape Agulhas. '
                        'Because it is <strong>E</strong>, it is a line of longitude east of the Prime Meridian.</li></ul>'
                        '<p><strong>Check:</strong> 45° N - latitude or longitude? <em>Latitude, because it has N.</em></p>'
                    ),
                },
                'video': {'id': 'cwUuVdF8ohY',
                          'title': 'What Are Latitude & Longitude? | Locating Places On Earth | The Dr Binocs Show | Peekaboo Kidz',
                          'channel': 'Peekaboo Kidz', 'minutes': 5},
                'worksheet': {
                    'instructions': 'Answer the questions. Use an atlas if you have one.',
                    'exercises': [
                        '1. In which direction do lines of latitude run?',
                        '2. In which direction do lines of longitude run?',
                        '3. What is the latitude of the Equator? What is the latitude of the South Pole?',
                        '4. Give another name for lines of latitude and for lines of longitude.',
                        '5. Say whether each is latitude or longitude: 15° W, 26° S, 60° N, 31° E.',
                        '6. Where do all lines of longitude meet?',
                        '7. Why are latitude and longitude measured in degrees?',
                    ],
                },
                'quiz': [
                    ('mcq', 'Lines of latitude measure distance ...',
                     ['east or west of the Prime Meridian', 'north or south of the Equator', 'from the sea'], 1),
                    ('mcq', 'Which of these is a line of longitude?', ['30° S', '0° (Equator)', '28° E', '45° N'], 2),
                    ('tf', 'All lines of longitude meet at the North and South Poles.', True),
                    ('tf', 'The South Pole is at 180° S.', False),
                ],
                'homework': {
                    'title': 'Latitude or longitude?',
                    'instructions': 'Show the difference between latitude and longitude.',
                    'tasks': [
                        'Draw two circles. On one draw 5 lines of latitude; on the other draw 5 lines of longitude.',
                        'Label the Equator and the Prime Meridian.',
                        'Write one way to remember the difference between the two kinds of lines.',
                    ],
                    'marks': 10,
                },
            },
            {
                'title': 'Global addresses: finding places with coordinates',
                'minutes': 50,
                'objectives': [
                    'Learners will explain what a global address (coordinates) is.',
                    'Learners will give the approximate latitude and longitude of South African cities.',
                    'Learners will find a place on a map from its coordinates.',
                ],
                'notes': (
                    '<p>Every place on Earth has a <strong>global address</strong>, also called its '
                    '<strong>coordinates</strong>. It is written as <strong>latitude first, then longitude</strong>.</p>'
                    '<p>Approximate global addresses of South African cities:</p>'
                    '<ul><li><strong>Cape Town:</strong> 34° S, 18° E</li>'
                    '<li><strong>Durban:</strong> 30° S, 31° E</li>'
                    '<li><strong>Johannesburg:</strong> 26° S, 28° E</li>'
                    '<li><strong>Bloemfontein:</strong> 29° S, 26° E</li></ul>'
                    '<p>Notice that all South African places have <strong>S</strong> latitude (south of the '
                    'Equator) and <strong>E</strong> longitude (east of the Prime Meridian).</p>'
                    '<p><strong>How to find a place from coordinates:</strong></p>'
                    '<ol><li>Find the latitude line (N or S) on the side of the map.</li>'
                    '<li>Find the longitude line (E or W) along the top or bottom.</li>'
                    '<li>Follow both lines until they cross. The place is where they meet.</li></ol>'
                    '<p>Coordinates are used by pilots, ship captains, rescue teams and GPS on cell phones. '
                    'GPS uses very exact coordinates with decimals or minutes, such as 33.9° S, 18.4° E.</p>'
                ),
                'key_terms': [
                    ('coordinates', 'the latitude and longitude that give the exact position of a place'),
                    ('global address', 'the position of a place given by its latitude and longitude'),
                    ('GPS', 'Global Positioning System: uses satellites to find coordinates'),
                ],
                'example': {
                    'title': 'Worked example: whose city?',
                    'html': (
                        '<p><strong>Question:</strong> Which city is at about 30° S, 31° E?</p>'
                        '<ol><li>Find 30° S on the side of the atlas map of South Africa.</li>'
                        '<li>Find 31° E along the bottom.</li>'
                        '<li>Follow the lines to where they cross: on the east coast in KwaZulu-Natal.</li></ol>'
                        '<p><strong>Answer:</strong> Durban.</p>'
                        '<p><strong>Reverse:</strong> Cape Town is further south (34° S) and further west (18° E) than Durban.</p>'
                    ),
                },
                'video': {'id': 'FEKFRV29Sk4',
                          'title': 'Latitude and Longitude | Using Coordinates to Find Places on a Map',
                          'channel': 'Equatoro', 'minutes': 6},
                'worksheet': {
                    'instructions': 'Use an atlas or the notes to answer the questions.',
                    'exercises': [
                        '1. What is a global address?',
                        '2. Which is written first in a global address: latitude or longitude?',
                        '3. Give the approximate global address of Cape Town.',
                        '4. Which city is at about 26° S, 28° E?',
                        '5. Why do all places in South Africa have an S latitude and an E longitude?',
                        '6. Which city is further north: Durban or Johannesburg? How do you know?',
                        '7. Name two jobs where people use coordinates.',
                    ],
                },
                'quiz': [
                    ('mcq', 'In a global address, which comes first?', ['Longitude', 'Latitude', 'Altitude'], 1),
                    ('mcq', 'Which city is at about 34° S, 18° E?', ['Durban', 'Johannesburg', 'Polokwane', 'Cape Town'], 3),
                    ('tf', 'All places in South Africa have a latitude south of the Equator.', True),
                    ('mcq', 'Which global address could NOT be in South Africa?', ['29° S, 26° E', '30° S, 31° E', '30° N, 31° E'], 2),
                ],
                'homework': {
                    'title': 'Coordinate hunt',
                    'instructions': 'Use an atlas, a map, or a map app with an adult\'s help.',
                    'tasks': [
                        'Find the approximate latitude and longitude of the town or city nearest to where you live.',
                        'Find the coordinates of one other city in Africa and one city in another continent.',
                        'For each, write which two hemispheres it is in.',
                    ],
                    'marks': 12,
                },
            },
        ],
    },
    # -------------------------------------------------------------- LIFE-SK
    (4, 'LIFE-SK'): {
        'topic': 'Development of the self: personal strengths',
        'caps': 'Personal and Social Well-being Term 1: Development of the self - personal strengths, '
                'likes and dislikes; self-concept; respecting own and others\' strengths and differences',
        'summary': 'Learners think about who they are, discover their personal strengths and learn to '
                   'appreciate the strengths and differences of others.',
        'days': [
            {
                'title': 'Who am I?',
                'minutes': 30,
                'objectives': [
                    'I can describe myself: my looks, likes, dislikes and family.',
                    'I can explain that every person is unique.',
                    'I can share something about myself respectfully with the class.',
                ],
                'notes': (
                    '<p>Every person is <strong>unique</strong> - there is nobody exactly like you in the '
                    'whole world. Even twins have different thoughts, likes and fingerprints.</p>'
                    '<p>The picture you have of yourself is called your <strong>self-concept</strong>. It '
                    'includes:</p>'
                    '<ul><li>how you <strong>look</strong> (your hair, eyes, height),</li>'
                    '<li>what you <strong>like</strong> and <strong>dislike</strong> (food, games, music, subjects),</li>'
                    '<li>your <strong>family</strong>, culture, language and home,</li>'
                    '<li>what you are <strong>good at</strong> and what you are still learning.</li></ul>'
                    '<p>When you know yourself well, you can make good choices, set goals and understand '
                    'how you feel. A healthy self-concept means you accept yourself and believe you are '
                    'valuable, even when you make mistakes.</p>'
                    '<p>When others share about themselves, we <strong>listen</strong> and show '
                    '<strong>respect</strong>. We do not laugh at what makes someone different.</p>'
                ),
                'key_terms': [
                    ('unique', 'one of a kind; there is no one else exactly the same'),
                    ('self-concept', 'the picture or idea you have of yourself'),
                    ('respect', 'treating others and yourself with care and kindness'),
                ],
                'example': {
                    'title': 'Class activity: "All about me" hand',
                    'html': (
                        '<p>Trace your hand on a page.</p>'
                        '<ul><li>Thumb: your name and age.</li><li>Pointer finger: a food you like.</li>'
                        '<li>Middle finger: something you dislike.</li><li>Ring finger: someone special in your family.</li>'
                        '<li>Little finger: something you are good at.</li></ul>'
                        '<p>Share your hand with a partner. Find one way you are the same and one way you are different.</p>'
                    ),
                },
                'video': {'id': 'wRhVP3KH9oM',
                          'title': '💡 GET TO KNOW YOURSELF BETTER: Self-awareness, Self-image, and Self-esteem for Kids 💖🧠',
                          'channel': 'Smile and Learn - English', 'minutes': 5},
                'worksheet': {
                    'instructions': 'Complete each sentence about yourself.',
                    'exercises': [
                        '1. My name is ... and I am ... years old.',
                        '2. Three words that describe me are ...',
                        '3. My favourite food is ... and I do not like ...',
                        '4. My favourite game or sport is ...',
                        '5. Someone special in my family is ... because ...',
                        '6. One thing that makes me unique is ...',
                    ],
                },
                'quiz': [
                    ('mcq', 'The picture you have of yourself is called your ...', ['self-concept', 'shadow', 'timetable'], 0),
                    ('tf', 'Every person is unique.', True),
                    ('tf', 'It is fine to laugh at someone because they like different things.', False),
                ],
                'homework': {
                    'title': 'My "about me" poster',
                    'instructions': 'Make a small poster about yourself.',
                    'tasks': [
                        'Draw a picture of yourself in the middle of a page.',
                        'Around it, write or draw 6 things about you: likes, dislikes, family, talents.',
                    ],
                    'marks': 10,
                },
            },
            {
                'title': 'Discovering my strengths',
                'minutes': 30,
                'objectives': [
                    'I can explain what a personal strength is.',
                    'I can name at least three of my own strengths.',
                    'I can name something I want to improve and one way to work on it.',
                ],
                'notes': (
                    '<p>A <strong>strength</strong> is something you are good at or a good quality you have. '
                    'Everyone has strengths, but they are different for each person.</p>'
                    '<p>Strengths can be:</p>'
                    '<ul><li><strong>Skills and talents</strong> - drawing, singing, running, reading, maths, '
                    'building things, cooking.</li>'
                    '<li><strong>Character strengths</strong> - being kind, honest, brave, patient, helpful, '
                    'funny or a good friend.</li></ul>'
                    '<p>We also all have things we find hard. These are not "bad" - they are things we are '
                    '<strong>still learning</strong>. With practice and effort we can get better. Instead of '
                    'saying "I can\'t do it", we can say "I can\'t do it <em>yet</em>".</p>'
                    '<p>Knowing your strengths helps you feel <strong>confident</strong>. You can use your '
                    'strengths to help others and to work on the things you find difficult. For example, '
                    'a learner who is patient can use patience to practise reading every day.</p>'
                ),
                'key_terms': [
                    ('strength', 'something you are good at or a good quality you have'),
                    ('talent', 'a natural ability to do something well'),
                    ('confidence', 'believing in yourself and what you can do'),
                ],
                'example': {
                    'title': 'Class activity: strength spotting',
                    'html': (
                        '<p>In groups of four, each learner writes their name at the top of a page. Pass the '
                        'pages around. Each group member writes one <strong>kind</strong> strength they have '
                        'noticed in that person, e.g. "You always share" or "You are good at soccer".</p>'
                        '<p>Read your page. Did your friends notice strengths you did not know you had?</p>'
                    ),
                },
                'video': {'id': 'NECYgTscA5s',
                          'title': 'Dr. Panda 🏀 Discovering Your Strengths with Olette | Kids Learning Video',
                          'channel': 'Dr. Panda - Scholastic', 'minutes': 4},
                'worksheet': {
                    'instructions': 'Think carefully about yourself and answer honestly.',
                    'exercises': [
                        '1. What is a strength?',
                        '2. Write three skills or talents you have.',
                        '3. Write two character strengths you have (e.g. kind, honest).',
                        '4. Write one thing you are still learning to do.',
                        '5. Change this sentence to show a "yet" attitude: "I can\'t swim."',
                        '6. How can one of your strengths help someone else?',
                    ],
                },
                'quiz': [
                    ('mcq', 'Which of these is a character strength?', ['Being kind', 'Having long hair', 'Owning a bicycle'], 0),
                    ('tf', 'Only some people have strengths.', False),
                    ('mcq', 'What is a better thing to say than "I can\'t do it"?',
                     ['"I will never do it"', '"I can\'t do it yet"', '"It is stupid"'], 1),
                    ('tf', 'Practice and effort can help us improve at things we find hard.', True),
                ],
                'homework': {
                    'title': 'Strength interview',
                    'instructions': 'Ask a family member or caregiver about your strengths.',
                    'tasks': [
                        'Ask: "What do you think I am good at?" Write down their answer.',
                        'Ask them about one of their own strengths and write it down.',
                        'Write one goal for something you want to get better at this term.',
                    ],
                    'marks': 10,
                },
            },
            {
                'title': 'Respecting others\' strengths and differences',
                'minutes': 30,
                'objectives': [
                    'I can explain why people have different strengths and differences.',
                    'I can show respect for people who are different from me.',
                    'I can say how different strengths help a team.',
                ],
                'notes': (
                    '<p>People are different in many ways: how they look, their language, culture, religion, '
                    'family, abilities and what they enjoy. Some people use a wheelchair, glasses or a hearing aid. '
                    'Our differences make our class and our country interesting. South Africa is often called '
                    'the <strong>Rainbow Nation</strong> because of its many cultures and 12 official languages.</p>'
                    '<p>Just as you have strengths, so does every other person. In a team, different strengths '
                    'fit together like puzzle pieces. In a group project one learner may be good at drawing, '
                    'another at writing and another at keeping everyone organised.</p>'
                    '<p>We show <strong>respect</strong> for others by:</p>'
                    '<ul><li>listening when they speak,</li><li>using kind words and never teasing or bullying,</li>'
                    '<li>including everyone in games,</li><li>praising others when they do well,</li>'
                    '<li>being patient when someone finds something hard.</li></ul>'
                    '<p>Remember: being different is not better or worse. It is just different.</p>'
                ),
                'key_terms': [
                    ('difference', 'a way in which people or things are not the same'),
                    ('include', 'to let someone take part and belong'),
                    ('bullying', 'hurting or frightening someone again and again on purpose'),
                ],
                'example': {
                    'title': 'Class activity: the strength puzzle (with movement)',
                    'html': (
                        '<p>In groups of four, plan a short relay obstacle course in the playground '
                        '(PE): one learner designs the route, one keeps time, one explains the rules and one '
                        'leads the warm-up. Everyone runs the course.</p>'
                        '<p>Afterwards discuss: Which strengths did each person bring? Could one person have '
                        'done all the jobs as well alone?</p>'
                    ),
                },
                'video': {'id': '20qg8YfL894',
                          'title': '🎥🌍 What Makes Us UNIQUE? | Educational Videos for Primary School Kids @HappyLearningENG',
                          'channel': 'Happy Learning English', 'minutes': 4},
                'worksheet': {
                    'instructions': 'Answer the questions in full sentences.',
                    'exercises': [
                        '1. Name three ways people can be different from each other.',
                        '2. Why is South Africa called the Rainbow Nation?',
                        '3. Write three ways you can show respect to someone who is different from you.',
                        '4. A new learner speaks a different language. How can you make them feel welcome?',
                        '5. How do different strengths help a team?',
                        '6. What should you do if you see someone being teased?',
                    ],
                },
                'quiz': [
                    ('tf', 'Being different makes a person worse than others.', False),
                    ('mcq', 'Which is a way to show respect?', ['Teasing', 'Leaving someone out', 'Listening when they speak', 'Laughing at mistakes'], 2),
                    ('mcq', 'How many official languages does South Africa have?', ['9', '11', '12', '15'], 2),
                    ('tf', 'In a team, different strengths can work together like puzzle pieces.', True),
                ],
                'homework': {
                    'title': 'Kindness card',
                    'instructions': 'Make a card for someone in your family or class.',
                    'tasks': [
                        'Write the person\'s name and two strengths you admire in them.',
                        'Decorate the card and give it to the person.',
                    ],
                    'marks': 5,
                },
            },
        ],
    },
    (5, 'LIFE-SK'): {
        'topic': 'Development of the self: positive self-concept',
        'caps': 'Personal and Social Well-being Term 1: Development of the self - positive self-concept '
                'formation; acknowledging own strengths and those of others; respecting differences',
        'summary': 'Learners explore how a positive self-concept is formed, practise positive self-talk '
                   'and a growth mindset, and learn to value their own and others\' differences.',
        'days': [
            {
                'title': 'Self-concept and self-esteem',
                'minutes': 30,
                'objectives': [
                    'Learners will explain the meaning of self-concept and self-esteem.',
                    'Learners will identify things that build or break down self-esteem.',
                    'Learners will practise positive self-talk.',
                ],
                'notes': (
                    '<p>Your <strong>self-concept</strong> is how you see yourself: your idea of who you are, '
                    'what you are like and what you can do. <strong>Self-esteem</strong> is how you '
                    '<strong>feel</strong> about yourself - how much you value and like yourself.</p>'
                    '<p>A <strong>positive self-concept</strong> is formed by:</p>'
                    '<ul><li>what you <strong>tell yourself</strong> (your self-talk),</li>'
                    '<li>what <strong>other people</strong> say and how they treat you - family, friends, teachers,</li>'
                    '<li>your <strong>experiences</strong> of success and of trying again after failing.</li></ul>'
                    '<p>Things that build self-esteem: praise for effort, kind friends, learning new skills, '
                    'helping others. Things that break it down: being teased or bullied, comparing yourself '
                    'with others all the time, and negative self-talk.</p>'
                    '<p><strong>Positive self-talk</strong> means speaking to yourself like a good friend '
                    'would. Instead of "I am so stupid", say "I made a mistake, and I can learn from it." '
                    'People with healthy self-esteem are not boastful - they accept themselves and also respect others.</p>'
                ),
                'key_terms': [
                    ('self-concept', 'how you see yourself'),
                    ('self-esteem', 'how you feel about and value yourself'),
                    ('self-talk', 'the things you say to yourself in your mind'),
                ],
                'example': {
                    'title': 'Guided activity: flip the thought',
                    'html': (
                        '<p>Change each negative thought into positive self-talk:</p>'
                        '<ul><li>"I\'m useless at maths." <em>-&gt; "Maths is hard for me, but I get better when I practise."</em></li>'
                        '<li>"Nobody likes me." <em>-&gt; "I am a good friend, and I can join in and meet new people."</em></li>'
                        '<li>"I always mess up." <em>-&gt; "Everyone makes mistakes. I will try again."</em></li></ul>'
                        '<p>Now write one of your own.</p>'
                    ),
                },
                'video': {'id': '5BuHC8wBdBU',
                          'title': 'Self-Esteem For Kids - 10 Ways To Build Self-Esteem & Self-Confidence',
                          'channel': 'Mental Health Center Kids', 'minutes': 6},
                'worksheet': {
                    'instructions': 'Answer the questions in full sentences.',
                    'exercises': [
                        '1. What is the difference between self-concept and self-esteem?',
                        '2. Name three things that help to build self-esteem.',
                        '3. Name two things that can break down self-esteem.',
                        '4. Change into positive self-talk: "I will never be good at sport."',
                        '5. Write three positive sentences about yourself that start with "I am ...".',
                        '6. How can you help a friend who has low self-esteem?',
                    ],
                },
                'quiz': [
                    ('mcq', 'How you feel about and value yourself is called ...', ['self-esteem', 'self-defence', 'selfishness'], 0),
                    ('tf', 'Positive self-talk means talking to yourself as a good friend would.', True),
                    ('mcq', 'Which can break down self-esteem?', ['Praise for effort', 'Being bullied', 'Learning a new skill', 'Helping others'], 1),
                    ('tf', 'Having healthy self-esteem means boasting that you are better than everyone.', False),
                ],
                'homework': {
                    'title': 'Positive self-talk cards',
                    'instructions': 'Make cards to encourage yourself.',
                    'tasks': [
                        'Write 4 positive self-talk sentences on small cards or pieces of paper.',
                        'Put them where you will see them (e.g. your schoolbag) and read them every day this week.',
                    ],
                    'marks': 8,
                },
            },
            {
                'title': 'Growing my abilities: a growth mindset',
                'minutes': 30,
                'objectives': [
                    'Learners will acknowledge their own strengths and achievements.',
                    'Learners will explain the difference between a fixed and a growth mindset.',
                    'Learners will set a simple personal goal with steps.',
                ],
                'notes': (
                    '<p>Part of a positive self-concept is <strong>acknowledging</strong> (recognising) your '
                    'strengths and achievements - big and small. Learning to ride a bicycle, reading a whole '
                    'book or helping at home are all achievements.</p>'
                    '<p>People think about their abilities in two ways:</p>'
                    '<ul><li>A <strong>fixed mindset</strong>: "I am either clever or not. I can\'t change." '
                    'People with this mindset often give up when things get hard.</li>'
                    '<li>A <strong>growth mindset</strong>: "My brain can grow. With effort, good strategies '
                    'and help, I can improve." People with this mindset see mistakes as part of learning.</li></ul>'
                    '<p>The brain is like a muscle: the more you practise, the stronger it gets. The little '
                    'word <strong>"yet"</strong> is powerful: "I can\'t do long division <em>yet</em>."</p>'
                    '<p>A <strong>goal</strong> helps you grow. A good goal is clear and has small steps, for '
                    'example: <em>Goal: read better. Steps: read for 15 minutes every night; ask for help '
                    'with new words; keep a list of books I finish.</em></p>'
                ),
                'key_terms': [
                    ('achievement', 'something you have done successfully through effort'),
                    ('fixed mindset', 'believing your abilities cannot change'),
                    ('growth mindset', 'believing you can improve your abilities through effort and learning'),
                    ('goal', 'something you plan and work to achieve'),
                ],
                'example': {
                    'title': 'Guided activity: fixed or growth?',
                    'html': (
                        '<p>Sort each statement as F (fixed) or G (growth):</p>'
                        '<ol><li>"This is too hard, I give up." <em>(F)</em></li>'
                        '<li>"I will try a different way." <em>(G)</em></li>'
                        '<li>"Mistakes help me learn." <em>(G)</em></li>'
                        '<li>"I\'m just not a sporty person." <em>(F)</em></li></ol>'
                        '<p>Then list three things you can do now that you could not do when you were in Grade 1.</p>'
                    ),
                },
                'video': {'id': 'w6LLxTcVN9k',
                          'title': 'Growth Mindset For Kids-Growth Mindset vs. Fixed Mindset-The Power Of Yet-Elementary-Middle School',
                          'channel': 'Mental Health Center Kids', 'minutes': 6},
                'worksheet': {
                    'instructions': 'Answer the questions and complete the goal plan.',
                    'exercises': [
                        '1. Write three achievements you are proud of.',
                        '2. Explain the difference between a fixed and a growth mindset.',
                        '3. Change into growth mindset: "I am bad at drawing."',
                        '4. Why can mistakes be helpful?',
                        '5. Write one goal for this term.',
                        '6. Write three small steps to reach your goal.',
                    ],
                },
                'quiz': [
                    ('tf', 'A growth mindset means believing you can improve with effort.', True),
                    ('mcq', 'Which statement shows a growth mindset?',
                     ['"I give up."', '"I\'m not clever enough."', '"I can\'t do it yet, but I will keep trying."'], 2),
                    ('mcq', 'A good goal should ...', ['be vague', 'have clear, small steps', 'be done by someone else'], 1),
                    ('tf', 'People with a growth mindset never make mistakes.', False),
                ],
                'homework': {
                    'title': 'My goal tracker',
                    'instructions': 'Work on the goal you set in class.',
                    'tasks': [
                        'Draw a table for 5 days. Each day, tick when you did a step towards your goal.',
                        'At the end, write two sentences on how it went.',
                    ],
                    'marks': 10,
                },
            },
            {
                'title': 'Valuing differences in others',
                'minutes': 30,
                'objectives': [
                    'Learners will acknowledge the strengths of others.',
                    'Learners will explain why respecting differences is important.',
                    'Learners will describe how to respond to unfair treatment of others.',
                ],
                'notes': (
                    '<p>Just as you have strengths, every person around you has strengths too. A positive '
                    'self-concept does not mean thinking you are better than others. People with healthy '
                    'self-esteem can <strong>celebrate others\' successes</strong>.</p>'
                    '<p>People differ in <strong>appearance</strong>, <strong>language</strong>, '
                    '<strong>culture</strong>, <strong>religion</strong>, <strong>abilities and disabilities</strong>, '
                    '<strong>family types</strong> and <strong>interests</strong>. The South African '
                    'Constitution says that everyone has equal dignity and that nobody may be treated unfairly '
                    'because of their race, gender, religion, disability, language or culture.</p>'
                    '<p><strong>Stereotypes</strong> are unfair ideas that all people in a group are the same, '
                    'for example "girls can\'t play soccer" or "boys don\'t cry". Stereotypes are hurtful and untrue.</p>'
                    '<p>If someone is treated unfairly or bullied:</p>'
                    '<ul><li>do not join in or laugh,</li><li>be kind to the person who is hurt,</li>'
                    '<li>tell a trusted adult such as a teacher or parent.</li></ul>'
                ),
                'key_terms': [
                    ('dignity', 'the value and worth every person has'),
                    ('stereotype', 'an unfair idea that all people in a group are the same'),
                    ('discrimination', 'treating someone unfairly because of who they are'),
                ],
                'example': {
                    'title': 'Class activity: compliments circle',
                    'html': (
                        '<p>Sit in a circle. Each learner says one sincere compliment about the strength of '
                        'the person on their right, e.g. "Thandi, you are always fair when we play games."</p>'
                        '<p>Then discuss these stereotypes and why they are untrue: "Only boys are good at '
                        'maths." "Older people can\'t use computers."</p>'
                    ),
                },
                'video': {'id': 'bgWe5cqFJ68',
                          'title': 'What Makes Us Unique: Celebrating Our Differences and Magic of Diversity',
                          'channel': 'Happy Harbor Kids Learning', 'minutes': 5},
                'worksheet': {
                    'instructions': 'Answer the questions in full sentences.',
                    'exercises': [
                        '1. Name three strengths of a classmate or friend.',
                        '2. List four ways in which people can be different.',
                        '3. What is a stereotype? Give one example and explain why it is unfair.',
                        '4. What does the Constitution say about treating people unfairly?',
                        '5. What three things should you do if you see someone being bullied?',
                        '6. Why is it good to celebrate other people\'s successes?',
                    ],
                },
                'quiz': [
                    ('mcq', 'An unfair idea that all people in a group are the same is a ...', ['compliment', 'stereotype', 'goal'], 1),
                    ('tf', 'People with healthy self-esteem can celebrate other people\'s successes.', True),
                    ('mcq', 'What should you do if you see someone being bullied?',
                     ['Laugh along', 'Ignore it completely', 'Tell a trusted adult', 'Join in'], 2),
                    ('tf', 'The Constitution allows people to be treated unfairly because of their language.', False),
                ],
                'homework': {
                    'title': 'A person I admire',
                    'instructions': 'Write about someone who is different from you in some way and whom you admire.',
                    'tasks': [
                        'Write a paragraph (5-7 sentences) about the person and two of their strengths.',
                        'Explain one thing you have learnt from this person.',
                    ],
                    'marks': 10,
                },
            },
        ],
    },
    (6, 'LIFE-SK'): {
        'topic': 'Development of the self: self-concept, achievements and emotions',
        'caps': 'Personal and Social Well-being Term 1: Development of the self - positive self-concept '
                'formation; acknowledging own achievements; dealing with emotions; respecting differences',
        'summary': 'Learners reflect on their achievements and self-image, learn healthy ways to '
                   'recognise and handle emotions, and practise respecting differences.',
        'days': [
            {
                'title': 'My achievements and self-image',
                'minutes': 30,
                'objectives': [
                    'Learners will identify and acknowledge their own achievements.',
                    'Learners will explain how influences such as friends, family and media shape self-image.',
                    'Learners will describe ways to build a realistic, positive self-concept.',
                ],
                'notes': (
                    '<p>As you grow older, the way you see yourself (<strong>self-concept</strong>) and how you '
                    'feel about how you look (<strong>body image</strong>) can change. Many influences shape '
                    'your self-image:</p>'
                    '<ul><li><strong>Family</strong> - encouragement and the values you learn at home.</li>'
                    '<li><strong>Friends and peers</strong> - what they say and whether they accept you.</li>'
                    '<li><strong>Media and social media</strong> - adverts and edited photos often show '
                    '"perfect" people who are not realistic.</li>'
                    '<li><strong>Your own achievements</strong> - the things you have worked hard for.</li></ul>'
                    '<p>Taking time to <strong>acknowledge your achievements</strong> builds confidence. '
                    'Achievements are not only trophies or top marks. They include learning a new skill, '
                    'improving a mark, standing up for a friend, finishing a difficult task or overcoming a fear.</p>'
                    '<p>A <strong>realistic, positive self-concept</strong> means you know your strengths, '
                    'accept your weaknesses, and know you can keep growing. Avoid comparing yourself all the '
                    'time to others - compare yourself with who you were last year.</p>'
                ),
                'key_terms': [
                    ('achievement', 'something you accomplished through effort'),
                    ('body image', 'how you see and feel about your body'),
                    ('influence', 'something that affects how you think, feel or act'),
                ],
                'example': {
                    'title': 'Class activity: achievement timeline',
                    'html': (
                        '<p>Draw a line across a page from "Born" to "Grade 6". Mark at least five achievements '
                        'along the line, for example: "Age 6 - learnt to swim", "Grade 3 - read my first '
                        'chapter book", "Grade 5 - helped my gran plant a vegetable garden".</p>'
                        '<p>Circle the achievement that took the most effort. What helped you succeed?</p>'
                    ),
                },
                'video': {'id': 'pdjaxS4ME2A', 'title': 'Wellbeing For Children: Confidence And Self-Esteem',
                          'channel': 'ClickView', 'minutes': 5},
                'worksheet': {
                    'instructions': 'Answer the questions thoughtfully.',
                    'exercises': [
                        '1. List five of your achievements (they do not have to be awards).',
                        '2. Name four influences on a person\'s self-image.',
                        '3. How can social media give children an unrealistic idea of how they should look?',
                        '4. What does a realistic, positive self-concept mean?',
                        '5. Why is it better to compare yourself with who you were last year than with others?',
                        '6. Write one thing you would like to achieve by the end of Grade 6.',
                    ],
                },
                'quiz': [
                    ('tf', 'Achievements include improving at something, not only winning trophies.', True),
                    ('mcq', 'Which influence often shows edited, unrealistic pictures of people?',
                     ['A grandparent', 'Advertising and social media', 'A school library'], 1),
                    ('mcq', 'How you see and feel about your body is called your ...',
                     ['body image', 'body language', 'body clock', 'body temperature'], 0),
                    ('tf', 'A positive self-concept means believing you have no weaknesses.', False),
                ],
                'homework': {
                    'title': 'Letter to my future self',
                    'instructions': 'Write a short letter to yourself to open at the end of the year.',
                    'tasks': [
                        'Mention three achievements you are proud of so far.',
                        'Describe two goals for this year and one strength that will help you reach them.',
                    ],
                    'marks': 10,
                },
            },
            {
                'title': 'Understanding and handling emotions',
                'minutes': 30,
                'objectives': [
                    'Learners will name a range of emotions and how they show in the body.',
                    'Learners will explain that all emotions are normal but actions are choices.',
                    'Learners will practise healthy coping strategies for strong emotions.',
                ],
                'notes': (
                    '<p><strong>Emotions</strong> (feelings) such as happiness, sadness, anger, fear, '
                    'excitement, jealousy and embarrassment are a normal part of life. As you approach your '
                    'teenage years, your emotions may change more quickly and feel stronger.</p>'
                    '<p>Emotions show in our bodies: anger can make your face hot and fists tight; fear can '
                    'make your heart beat fast; sadness can make you feel tired or tearful. Noticing these '
                    'signs helps you <strong>name</strong> the feeling.</p>'
                    '<p>All feelings are allowed, but <strong>what we do</strong> with them is a choice. '
                    'Hitting, shouting or breaking things hurts others and ourselves. Healthy '
                    '<strong>coping strategies</strong> include:</p>'
                    '<ul><li>stop and take slow, deep breaths (breathe in for 4, out for 4),</li>'
                    '<li>count to 10 or walk away for a short time,</li>'
                    '<li>talk to someone you trust,</li><li>write or draw how you feel,</li>'
                    '<li>do physical activity, like running, skipping or dancing,</li>'
                    '<li>use "I" messages: "I feel upset when you take my things without asking."</li></ul>'
                ),
                'key_terms': [
                    ('emotion', 'a feeling such as joy, anger, fear or sadness'),
                    ('coping strategy', 'a healthy way to deal with a strong feeling or problem'),
                    ('"I" message', 'a calm way to say how you feel: "I feel ... when ..."'),
                ],
                'example': {
                    'title': 'Guided activity: what could you do?',
                    'html': (
                        '<p><strong>Scenario:</strong> Sipho\'s friend posts a joke about him in the class '
                        'group chat and everyone laughs. Sipho feels angry and embarrassed.</p>'
                        '<ol><li>Name the emotions: anger, embarrassment.</li>'
                        '<li>Unhelpful reaction: posting something nasty back.</li>'
                        '<li>Healthy choices: take deep breaths and log off; later use an "I" message: '
                        '"I felt hurt when you posted that joke. Please take it down."; talk to a parent or teacher.</li></ol>'
                    ),
                },
                'video': {'id': 'Vs-MyQgfH3A',
                          'title': 'Coping Skills For Kids - Managing Feelings & Emotions For Elementary-Middle School | Self-Regulation',
                          'channel': 'Mental Health Center Kids', 'minutes': 6},
                'worksheet': {
                    'instructions': 'Answer the questions in full sentences.',
                    'exercises': [
                        '1. Name six different emotions.',
                        '2. Describe how anger or fear can show in your body.',
                        '3. Explain this statement: "All feelings are allowed, but actions are choices."',
                        '4. List four healthy coping strategies.',
                        '5. Write an "I" message for: your brother keeps using your pens without asking.',
                        '6. Who are two trusted people you can talk to when you feel upset?',
                    ],
                },
                'quiz': [
                    ('tf', 'It is normal to feel angry or sad sometimes.', True),
                    ('mcq', 'Which is a healthy coping strategy?',
                     ['Breaking something', 'Taking slow, deep breaths', 'Shouting at a friend', 'Keeping it secret forever'], 1),
                    ('mcq', 'Which is an "I" message?',
                     ['"You always ruin everything!"', '"I feel upset when you shout at me."', '"Go away!"'], 1),
                    ('tf', 'Strong emotions mean you are allowed to hurt others.', False),
                ],
                'homework': {
                    'title': 'Feelings journal',
                    'instructions': 'Keep a short feelings journal for three days.',
                    'tasks': [
                        'Each day, write one emotion you felt and what caused it.',
                        'Write what you did about the feeling and whether it was a healthy choice.',
                    ],
                    'marks': 9,
                },
            },
            {
                'title': 'Respecting differences and building others up',
                'minutes': 30,
                'objectives': [
                    'Learners will explain the link between their own self-concept and how they treat others.',
                    'Learners will identify prejudice and discrimination.',
                    'Learners will plan actions to make others feel included and valued.',
                ],
                'notes': (
                    '<p>How we feel about ourselves affects how we treat others. People who feel secure in '
                    'themselves are more likely to be kind and to <strong>build others up</strong>. People who '
                    'feel bad about themselves sometimes put others down to feel better.</p>'
                    '<p><strong>Prejudice</strong> is judging someone before you know them, only because of a '
                    'group they belong to. When prejudice turns into action - leaving people out, insulting '
                    'them or treating them unfairly - it is <strong>discrimination</strong>. The Bill of '
                    'Rights in the South African Constitution protects everyone\'s right to '
                    '<strong>equality</strong> and <strong>human dignity</strong>.</p>'
                    '<p>Ways to respect differences and build others up:</p>'
                    '<ul><li>get to know people before forming opinions,</li>'
                    '<li>learn a greeting in a classmate\'s home language,</li>'
                    '<li>include learners with disabilities in games and group work, adapting activities where needed,</li>'
                    '<li>give genuine compliments and encouragement,</li>'
                    '<li>speak up (safely) or report when someone is discriminated against.</li></ul>'
                ),
                'key_terms': [
                    ('prejudice', 'judging someone unfairly before knowing them'),
                    ('discrimination', 'treating someone unfairly because of who they are'),
                    ('equality', 'everyone having the same rights and value'),
                    ('inclusion', 'making sure everyone can take part and belong'),
                ],
                'example': {
                    'title': 'Class activity: inclusive game (PE)',
                    'html': (
                        '<p>Play a passing game in the playground with a ball. Then change the rules so that '
                        'everyone can take part, e.g. a learner on crutches or who cannot see well.</p>'
                        '<ul><li>Use a bigger, brighter or bell ball.</li>'
                        '<li>Roll the ball instead of throwing it.</li>'
                        '<li>Make the area smaller and say the name of the person you pass to.</li></ul>'
                        '<p>Discuss: How did changing the rules make the game fairer for everyone?</p>'
                    ),
                },
                'video': {'id': 'om3INBWfoxY', 'title': 'Wellbeing For Children: Identity And Values',
                          'channel': 'ClickView', 'minutes': 5},
                'worksheet': {
                    'instructions': 'Answer the questions in full sentences.',
                    'exercises': [
                        '1. How can the way you feel about yourself affect how you treat others?',
                        '2. What is the difference between prejudice and discrimination?',
                        '3. Which two rights in the Bill of Rights protect people from discrimination?',
                        '4. Give three ways to make a new learner from another country feel included.',
                        '5. How can a game be changed so that a learner who uses a wheelchair can join in?',
                        '6. Write a genuine compliment you could give a classmate this week.',
                    ],
                },
                'quiz': [
                    ('mcq', 'Judging someone before knowing them, because of their group, is ...',
                     ['inclusion', 'prejudice', 'equality'], 1),
                    ('tf', 'Leaving someone out of a game because of their language is a form of discrimination.', True),
                    ('mcq', 'Which action builds others up?',
                     ['Gossiping', 'Giving genuine encouragement', 'Copying their work', 'Ignoring them'], 1),
                    ('tf', 'The Bill of Rights protects the right to equality and human dignity.', True),
                ],
                'homework': {
                    'title': 'Kindness challenge',
                    'instructions': 'Do three acts of kindness or inclusion during the next week.',
                    'tasks': [
                        'Record each act: what you did, for whom (first name only), and how the person reacted.',
                        'Write two sentences on how doing these acts made you feel.',
                    ],
                    'marks': 10,
                },
            },
        ],
    },
    # --------------------------------------------------------------- CODING
    (4, 'CODING'): {
        'topic': 'Algorithms and sequencing (unplugged)',
        'caps': 'Coding and Robotics (draft CAPS) Gr 4: Algorithms and coding - everyday algorithms, '
                'step-by-step instructions, sequencing, directional coding on a grid (unplugged)',
        'summary': 'Learners discover that an algorithm is a set of step-by-step instructions, see why the '
                   'order of steps matters and write arrow algorithms to move a "robot" on a grid.',
        'days': [
            {
                'title': 'What is an algorithm?',
                'minutes': 40,
                'objectives': [
                    'I can explain what an algorithm is.',
                    'I can give examples of algorithms in everyday life.',
                    'I can write a simple algorithm for a daily task.',
                ],
                'notes': (
                    '<p>An <strong>algorithm</strong> is a set of clear, <strong>step-by-step instructions</strong> '
                    'to complete a task or solve a problem. We use algorithms every day without noticing:</p>'
                    '<ul><li>a recipe for making a sandwich,</li><li>the steps for brushing your teeth,</li>'
                    '<li>directions to get to a friend\'s house,</li><li>instructions for building a Lego model.</li></ul>'
                    '<p>Computers and robots cannot think for themselves. They only do exactly what they are '
                    'told. A <strong>program</strong> is an algorithm written in a language a computer can '
                    'understand. The people who write programs are called <strong>programmers</strong> or coders.</p>'
                    '<p>A good algorithm:</p>'
                    '<ol><li>has a clear <strong>start</strong> and <strong>end</strong>,</li>'
                    '<li>has steps that are <strong>clear and exact</strong> - no guessing,</li>'
                    '<li>has steps in the <strong>right order</strong>,</li>'
                    '<li>solves the task every time it is followed.</li></ol>'
                    '<p>Today we will be "human robots" to see how exact instructions must be.</p>'
                ),
                'key_terms': [
                    ('algorithm', 'a set of step-by-step instructions to complete a task'),
                    ('program', 'an algorithm written in a language a computer understands'),
                    ('programmer', 'a person who writes computer programs'),
                ],
                'example': {
                    'title': 'Class activity: human robot',
                    'html': (
                        '<p>The teacher acts as a robot that follows instructions <em>exactly</em>. Learners '
                        'give instructions to make the robot sit down on a chair.</p>'
                        '<p>If a learner says "sit down", the robot asks: "Where? How?" A better algorithm:</p>'
                        '<ol><li>Start.</li><li>Turn to face the chair.</li><li>Take 3 steps forward.</li>'
                        '<li>Turn around.</li><li>Bend your knees and sit.</li><li>Stop.</li></ol>'
                    ),
                },
                'video': {'id': 'SiTSq2h1EaQ', 'title': 'What is an Algorithm? | All About Computers | Tynker',
                          'channel': 'Tynker', 'minutes': 3},
                'worksheet': {
                    'instructions': 'Answer the questions. Number the steps of your algorithms.',
                    'exercises': [
                        '1. What is an algorithm?',
                        '2. Give three examples of algorithms you follow every day.',
                        '3. Why must instructions for a computer be exact?',
                        '4. Write an algorithm with at least 5 steps for washing your hands.',
                        '5. Write an algorithm with at least 5 steps for making a cup of tea or juice.',
                        '6. What is the name for an algorithm written for a computer?',
                    ],
                },
                'quiz': [
                    ('mcq', 'An algorithm is ...', ['a type of robot', 'a set of step-by-step instructions', 'a computer screen'], 1),
                    ('tf', 'Computers can guess what you mean if your instructions are unclear.', False),
                    ('mcq', 'Which is an everyday example of an algorithm?', ['A recipe', 'A tree', 'A colour', 'A song title'], 0),
                    ('tf', 'A good algorithm has a clear start and end.', True),
                ],
                'homework': {
                    'title': 'Algorithm at home',
                    'instructions': 'Write an algorithm for a family member to follow.',
                    'tasks': [
                        'Write a step-by-step algorithm (6-10 steps) for a task, e.g. making a peanut butter sandwich.',
                        'Ask a family member to follow it EXACTLY. Write down one step you had to fix.',
                    ],
                    'marks': 10,
                },
            },
            {
                'title': 'Sequencing: order matters',
                'minutes': 40,
                'objectives': [
                    'I can explain what sequencing means.',
                    'I can put mixed-up steps into the correct order.',
                    'I can explain what happens when steps are in the wrong order.',
                ],
                'notes': (
                    '<p><strong>Sequencing</strong> means putting steps in the <strong>correct order</strong>. '
                    'In an algorithm, the order of the steps is very important. A computer follows steps one '
                    'at a time, from the top to the bottom.</p>'
                    '<p>Think about getting dressed. If you put your shoes on before your socks, the result is '
                    'wrong - even though all the steps are there! The same is true for computers: the right '
                    'steps in the wrong order give the wrong result.</p>'
                    '<p>Some steps <em>must</em> happen before others. For example, to plant a seed:</p>'
                    '<ol><li>Fill a pot with soil.</li><li>Make a small hole.</li><li>Put the seed in the hole.</li>'
                    '<li>Cover the seed with soil.</li><li>Water the soil.</li></ol>'
                    '<p>You cannot cover the seed before you put it in!</p>'
                    '<p>When a sequence gives the wrong result, we find and fix the mistake. A mistake in a '
                    'program is called a <strong>bug</strong>, and fixing it is called <strong>debugging</strong>.</p>'
                ),
                'key_terms': [
                    ('sequence', 'steps in a particular order'),
                    ('sequencing', 'putting steps into the correct order'),
                    ('bug', 'a mistake in an algorithm or program'),
                    ('debugging', 'finding and fixing mistakes'),
                ],
                'example': {
                    'title': 'Worked example: fix the sequence',
                    'html': (
                        '<p>These steps for brushing teeth are mixed up:</p>'
                        '<p>A. Rinse your mouth. B. Put toothpaste on the brush. C. Brush all your teeth for '
                        'two minutes. D. Wet the toothbrush. E. Pick up the toothbrush.</p>'
                        '<p><strong>Correct sequence:</strong> E, D, B, C, A.</p>'
                        '<p><strong>Why?</strong> You must pick up the brush before you can wet it, and you '
                        'rinse only after brushing.</p>'
                    ),
                },
                'video': {'id': 'zW3YZdPmCnM', 'title': 'Sequencing | Coding & Computer Science Song',
                          'channel': 'Scratch Garden', 'minutes': 3},
                'worksheet': {
                    'instructions': 'Put the steps in the correct order by writing the letters.',
                    'exercises': [
                        '1. Making toast: A. Eat the toast. B. Put bread in the toaster. C. Press the lever down. D. Spread butter on the toast. E. Take the toast out.',
                        '2. Posting a letter: A. Put the letter in the envelope. B. Write the letter. C. Post it. D. Write the address. E. Stick on a stamp.',
                        '3. Planting a seed: A. Water it. B. Fill the pot with soil. C. Put the seed in the hole. D. Make a hole. E. Cover the seed.',
                        '4. What happens if you put on your shoes before your socks?',
                        '5. What is a bug in a program?',
                        '6. Write your morning routine as a sequence of 6 steps.',
                    ],
                },
                'quiz': [
                    ('mcq', 'Sequencing means ...', ['drawing pictures', 'putting steps in the correct order', 'typing fast'], 1),
                    ('tf', 'If all the right steps are there, the order does not matter.', False),
                    ('mcq', 'A mistake in a program is called a ...', ['bug', 'loop', 'robot', 'sprite'], 0),
                    ('tf', 'A computer follows the steps of a program one at a time, in order.', True),
                ],
                'homework': {
                    'title': 'Comic strip sequence',
                    'instructions': 'Draw a 6-box comic strip that shows a task in the correct sequence.',
                    'tasks': [
                        'Choose a task (e.g. making a sandwich, getting ready for school) and draw 6 steps in order.',
                        'Cut out the boxes, mix them up and ask a family member to put them back in order.',
                    ],
                    'marks': 10,
                },
            },
            {
                'title': 'Arrow algorithms on a grid',
                'minutes': 40,
                'objectives': [
                    'I can write an algorithm using direction arrows to move along a grid.',
                    'I can follow an arrow algorithm and find where it ends.',
                    'I can find and fix a bug in an arrow algorithm.',
                ],
                'notes': (
                    '<p>Robots often move on a <strong>grid</strong> - a pattern of squares. We can control a '
                    'robot with simple direction <strong>commands</strong>:</p>'
                    '<ul><li><strong>Up</strong> - move one square up,</li>'
                    '<li><strong>Down</strong> - move one square down,</li>'
                    '<li><strong>Left</strong> - move one square left,</li>'
                    '<li><strong>Right</strong> - move one square right.</li></ul>'
                    '<p>We can write these as letters (U, D, L, R) or draw arrows. One arrow = one square. '
                    'An algorithm such as <strong>R R U U</strong> means: right, right, up, up.</p>'
                    '<p>When the same move is repeated, we can write it in a shorter way: '
                    '<strong>R R R</strong> can be written as <strong>3 x R</strong>. This is the start of '
                    'an idea called a <strong>loop</strong>.</p>'
                    '<p>There is often more than one correct algorithm to reach the same square. The '
                    '<strong>best</strong> algorithm is usually the shortest one that avoids obstacles.</p>'
                    '<p>If the robot ends up in the wrong place, trace the algorithm one step at a time with '
                    'your finger to find the bug.</p>'
                ),
                'key_terms': [
                    ('command', 'a single instruction given to a computer or robot'),
                    ('grid', 'a pattern of squares in rows and columns'),
                    ('obstacle', 'something that blocks the path'),
                ],
                'example': {
                    'title': 'Worked example: guide the robot to the battery',
                    'html': (
                        '<p>On a 5 x 5 grid the robot starts in the bottom-left square. The battery is 3 '
                        'squares to the right and 2 squares up. A rock is directly above the start square.</p>'
                        '<p><strong>Algorithm 1:</strong> R R R U U (5 steps) - works, avoids the rock.</p>'
                        '<p><strong>Algorithm 2:</strong> U U R R R - <em>bug!</em> The first U bumps into the rock.</p>'
                        '<p><strong>Short form of Algorithm 1:</strong> 3 x R, 2 x U.</p>'
                        '<p><em>Unplugged:</em> chalk a grid on the playground and take turns being the robot.</p>'
                    ),
                },
                'video': {'id': 'IfHmHZPxuV8', 'title': 'Unplugged: Human Coding Grid',
                          'channel': 'Meghan Zigmond', 'minutes': 4},
                'worksheet': {
                    'instructions': 'Draw a 6 x 6 grid. Mark START in the bottom-left square. Use U, D, L, R (one letter = one square).',
                    'exercises': [
                        '1. Follow R R U U U from START. Draw a star where you end.',
                        '2. Follow U U U U R R D from START. Draw a circle where you end.',
                        '3. Write an algorithm from START to the top-right square.',
                        '4. Write your answer to question 3 in short form (e.g. 5 x R).',
                        '5. A robot should go 2 right and 1 up, but the code is R U U. Find and fix the bug.',
                        '6. Put a rock 1 square to the right of START. Write an algorithm to reach 2 squares right of START without touching the rock.',
                    ],
                },
                'quiz': [
                    ('mcq', 'From START, the robot follows R R U. Where does it end?',
                     ['2 right, 1 up', '1 right, 2 up', '3 right', '2 up, 1 left'], 0),
                    ('mcq', 'Which is the short form of U U U U?', ['U x U', '4 x U', 'U4U'], 1),
                    ('tf', 'There can be more than one correct algorithm to reach the same square.', True),
                    ('tf', 'Tracing an algorithm step by step can help you find a bug.', True),
                ],
                'homework': {
                    'title': 'Design a grid maze',
                    'instructions': 'Make a grid maze puzzle for someone at home.',
                    'tasks': [
                        'Draw a 6 x 6 grid with a START, a FINISH and at least 4 obstacles.',
                        'Write the shortest algorithm from START to FINISH on the back.',
                        'Ask a family member to solve it and compare your algorithms.',
                    ],
                    'marks': 12,
                },
            },
        ],
    },
    (5, 'CODING'): {
        'topic': 'Precise algorithms, debugging and an introduction to Scratch',
        'caps': 'Coding and Robotics (draft CAPS) Gr 5: Algorithms and coding - precise instructions, '
                'sequencing, debugging; introduction to a block-based visual programming environment',
        'summary': 'Learners practise writing precise algorithms, learn to debug them, and are introduced '
                   'to Scratch: sprites, the stage and joining code blocks into a script.',
        'days': [
            {
                'title': 'Precise instructions',
                'minutes': 45,
                'objectives': [
                    'Learners will explain why algorithms must be precise and unambiguous.',
                    'Learners will improve vague instructions into precise ones.',
                    'Learners will write and test a precise algorithm with a partner.',
                ],
                'notes': (
                    '<p>Last year you learnt that an <strong>algorithm</strong> is a set of step-by-step '
                    'instructions. For a computer, instructions must be <strong>precise</strong> (exact) and '
                    '<strong>unambiguous</strong> (they can only mean one thing).</p>'
                    '<p>People can guess what you mean. Computers cannot. If you tell a person "put the '
                    'peanut butter on the bread", they know to open the jar and use a knife. A computer would '
                    'try to put the whole jar on the bread!</p>'
                    '<p>To make instructions precise:</p>'
                    '<ul><li>say <strong>exactly what</strong> object to use ("the blue cup", not "it"),</li>'
                    '<li>include <strong>how many</strong> or <strong>how far</strong> ("take 3 steps", not "walk a bit"),</li>'
                    '<li>give the <strong>direction</strong> ("turn left 90 degrees"),</li>'
                    '<li>do not skip "obvious" steps, like opening a lid,</li>'
                    '<li>use <strong>one action per step</strong>.</li></ul>'
                    '<p>Testing your algorithm with a partner who follows it exactly is the best way to find '
                    'missing or unclear steps.</p>'
                ),
                'key_terms': [
                    ('precise', 'exact and detailed'),
                    ('unambiguous', 'having only one possible meaning'),
                    ('input', 'information or instructions given to a computer'),
                    ('output', 'what the computer does or shows as a result'),
                ],
                'example': {
                    'title': 'Worked example: drawing by instructions',
                    'html': (
                        '<p><strong>Vague:</strong> "Draw a house."</p>'
                        '<p><strong>Precise:</strong></p>'
                        '<ol><li>Draw a square with sides of 4 cm in the middle of the page.</li>'
                        '<li>On top of the square, draw a triangle whose base is the top side of the square.</li>'
                        '<li>Inside the square, draw a rectangle 1 cm wide and 2 cm tall touching the bottom side, in the middle.</li></ol>'
                        '<p><em>Activity:</em> Back-to-back drawing - one partner reads precise steps, the other draws without seeing the picture. Compare!</p>'
                    ),
                },
                'video': {'id': 'FN2RM-CHkuI', 'title': 'Exact Instructions Challenge PB&J Classroom Friendly | Josh Darnit',
                          'channel': 'Josh Darnit', 'minutes': 4},
                'worksheet': {
                    'instructions': 'Rewrite the vague instructions so that they are precise.',
                    'exercises': [
                        '1. "Go to the door." (You are 5 steps from the door, which is on your left.)',
                        '2. "Make some juice." (Write at least 6 precise steps.)',
                        '3. "Draw a face." (Write precise steps with sizes and positions.)',
                        '4. What does unambiguous mean?',
                        '5. Why can a person follow vague instructions but a computer cannot?',
                        '6. Name two things you should always include to make an instruction precise.',
                    ],
                },
                'quiz': [
                    ('mcq', 'Which instruction is the most precise?',
                     ['"Walk a bit."', '"Go over there."', '"Take 4 steps forward."', '"Move."'], 2),
                    ('tf', 'Computers can work out what you meant when an instruction is unclear.', False),
                    ('mcq', '"Unambiguous" means ...', ['having only one meaning', 'very long', 'written in code'], 0),
                    ('tf', 'Testing an algorithm with a partner helps you find missing steps.', True),
                ],
                'homework': {
                    'title': 'Exact instructions challenge',
                    'instructions': 'Try the exact instructions challenge at home (with an adult\'s permission).',
                    'tasks': [
                        'Write precise steps for a simple task (e.g. making a bowl of cereal).',
                        'Have a family member follow them EXACTLY. Write down what went wrong and your improved steps.',
                    ],
                    'marks': 10,
                },
            },
            {
                'title': 'Debugging: finding and fixing errors',
                'minutes': 45,
                'objectives': [
                    'Learners will define a bug and debugging.',
                    'Learners will use a step-by-step strategy to find bugs in an algorithm.',
                    'Learners will correct buggy algorithms.',
                ],
                'notes': (
                    '<p>A <strong>bug</strong> is an error in an algorithm or program that makes it do '
                    'something we did not want. <strong>Debugging</strong> means finding and fixing bugs. '
                    'All programmers make mistakes - good programmers are good at debugging!</p>'
                    '<p>Common bugs:</p>'
                    '<ul><li>a step is in the <strong>wrong order</strong>,</li>'
                    '<li>a step is <strong>missing</strong>,</li>'
                    '<li>a step is <strong>wrong</strong> (e.g. left instead of right, 3 instead of 4),</li>'
                    '<li>there is an <strong>extra</strong> step that should not be there.</li></ul>'
                    '<p>A debugging strategy:</p>'
                    '<ol><li><strong>Predict:</strong> what should happen?</li>'
                    '<li><strong>Run/trace:</strong> follow the algorithm one step at a time.</li>'
                    '<li><strong>Spot:</strong> find the first step where the result goes wrong.</li>'
                    '<li><strong>Fix:</strong> change only that step.</li>'
                    '<li><strong>Test again</strong> to check that it works now.</li></ol>'
                    '<p>Debugging takes patience. Treat a bug as a puzzle to solve, not a failure.</p>'
                ),
                'key_terms': [
                    ('bug', 'an error in a program or algorithm'),
                    ('debugging', 'finding and fixing errors'),
                    ('trace', 'to follow an algorithm step by step to see what it does'),
                ],
                'example': {
                    'title': 'Worked example: debug the robot',
                    'html': (
                        '<p>A robot must go from START to the FLAG, which is 3 squares forward and then '
                        '2 squares to the right. The code is:</p>'
                        '<p>forward, forward, turn left, forward, forward, forward</p>'
                        '<p><strong>Trace:</strong> after two forwards it turns <em>left</em> - wrong. It also '
                        'moves only 2 forward before turning and 3 after.</p>'
                        '<p><strong>Fixed code:</strong> forward, forward, forward, turn right, forward, forward.</p>'
                        '<p>Two bugs were fixed: the turn direction, and the number of forward steps before and after the turn.</p>'
                    ),
                },
                'video': {'id': 'M6jokEIj4qQ',
                          'title': 'Free Coding tutorial for kids | What is Debugging ? | Debugging  for Kids | Debug code to fix bugs',
                          'channel': 'JrDinoCoders', 'minutes': 5},
                'worksheet': {
                    'instructions': 'Find and fix the bug in each algorithm. Say what kind of bug it is (wrong order, missing, wrong or extra step).',
                    'exercises': [
                        '1. Make tea: boil water, pour water into cup, put teabag in cup, drink, remove teabag.',
                        '2. Brush teeth: pick up brush, brush teeth, rinse mouth. (Something is missing.)',
                        '3. Robot must go 2 squares up: up, up, up.',
                        '4. Robot must go right 2 then down 1: right, right, up.',
                        '5. Write the five steps of the debugging strategy.',
                        '6. Why should you change only one step at a time when debugging?',
                    ],
                },
                'quiz': [
                    ('mcq', 'Finding and fixing errors in a program is called ...', ['looping', 'debugging', 'sorting', 'drawing'], 1),
                    ('tf', 'Good programmers never make mistakes.', False),
                    ('mcq', 'Robot code should move 2 squares up but is "up, up, up". What kind of bug is it?',
                     ['Missing step', 'Extra step', 'Wrong order'], 1),
                    ('tf', 'After fixing a bug, you should test the program again.', True),
                ],
                'homework': {
                    'title': 'Bug hunt',
                    'instructions': 'Create buggy algorithms for a family member to fix.',
                    'tasks': [
                        'Write a correct algorithm of 6 steps for an everyday task.',
                        'Copy it out again but add two bugs. Ask a family member to find them.',
                        'Write down whether they found both bugs and how.',
                    ],
                    'marks': 10,
                },
            },
            {
                'title': 'Meet Scratch: sprites, stage and blocks',
                'minutes': 45,
                'objectives': [
                    'Learners will identify the main parts of the Scratch screen.',
                    'Learners will explain what sprites, the stage and code blocks are.',
                    'Learners will build a short script that makes a sprite move and speak.',
                ],
                'notes': (
                    '<p><strong>Scratch</strong> is a free <strong>block-based</strong> programming language '
                    'made by MIT. Instead of typing code, you snap coloured <strong>blocks</strong> together '
                    'like puzzle pieces. It can be used online at scratch.mit.edu or offline.</p>'
                    '<p>The main parts of the Scratch screen:</p>'
                    '<ul>'
                    '<li><strong>Stage</strong> - the area where your program runs (top right).</li>'
                    '<li><strong>Sprites</strong> - the characters or objects that do things, e.g. the Scratch cat.</li>'
                    '<li><strong>Block palette</strong> - categories of blocks by colour: Motion (blue), '
                    'Looks (purple), Sound (pink), Events (yellow), Control (orange).</li>'
                    '<li><strong>Code area</strong> - where you drag and snap blocks together into a '
                    '<strong>script</strong>.</li>'
                    '<li><strong>Green flag</strong> to start the program, and the <strong>red stop sign</strong> to stop it.</li>'
                    '</ul>'
                    '<p>Blocks run from <strong>top to bottom</strong> - the same idea of <strong>sequence</strong> '
                    'you learnt with algorithms. A script usually starts with an Events block such as '
                    '<em>when green flag clicked</em>.</p>'
                ),
                'key_terms': [
                    ('Scratch', 'a free block-based programming language'),
                    ('sprite', 'a character or object that is programmed in Scratch'),
                    ('stage', 'the area where a Scratch program runs'),
                    ('script', 'a group of blocks snapped together'),
                ],
                'example': {
                    'title': 'Guided activity: my first script',
                    'html': (
                        '<p>Build this script for the cat sprite:</p>'
                        '<ol><li><em>when green flag clicked</em> (Events)</li>'
                        '<li><em>say Hello! for 2 seconds</em> (Looks)</li>'
                        '<li><em>move 100 steps</em> (Motion)</li>'
                        '<li><em>play sound Meow until done</em> (Sound)</li></ol>'
                        '<p>Click the green flag. Then swap blocks 2 and 3 - how does the order change what happens?</p>'
                        '<p><em>No computer?</em> Use paper "blocks" and act out the script.</p>'
                    ),
                },
                'video': {'id': '9jTPZfhuVro', 'title': 'Getting Started with Scratch',
                          'channel': 'Scratch Team', 'minutes': 3},
                'worksheet': {
                    'instructions': 'Answer the questions about Scratch.',
                    'exercises': [
                        '1. What is Scratch?',
                        '2. What is a sprite? What is the stage?',
                        '3. Which colour are Motion blocks? Which colour are Looks blocks?',
                        '4. Which block often starts a script?',
                        '5. In which order do Scratch blocks run?',
                        '6. Write a 4-block script that makes a sprite say "Sawubona!", move 50 steps and then say "Goodbye!".',
                    ],
                },
                'quiz': [
                    ('mcq', 'In Scratch, a character that you program is called a ...', ['stage', 'sprite', 'script', 'block'], 1),
                    ('mcq', 'Which button starts a Scratch program?', ['The red stop sign', 'The green flag', 'The delete key'], 1),
                    ('tf', 'Scratch blocks in a script run from top to bottom.', True),
                    ('mcq', 'Motion blocks such as "move 10 steps" are which colour?', ['Blue', 'Purple', 'Pink', 'Orange'], 0),
                ],
                'homework': {
                    'title': 'Plan a Scratch greeting',
                    'instructions': 'Plan (on paper) or build (on a device) a short Scratch greeting.',
                    'tasks': [
                        'Draw your sprite and the stage background you would choose.',
                        'Write a script of at least 5 blocks that starts with "when green flag clicked".',
                        'Explain what your sprite will do, in order.',
                    ],
                    'marks': 10,
                },
            },
        ],
    },
    (6, 'CODING'): {
        'topic': 'Scratch events and loops; introduction to robotics',
        'caps': 'Coding and Robotics (draft CAPS) Gr 6: Algorithms and coding - events, sequences and '
                'loops in a block-based environment; Robotics - what a robot is, input, process and output',
        'summary': 'Learners build event-driven Scratch scripts, use loops to repeat code efficiently, and '
                   'learn how robots use sensors, a controller and motors (input, process, output).',
        'days': [
            {
                'title': 'Events: making things happen in Scratch',
                'minutes': 45,
                'objectives': [
                    'Learners will explain what an event is in programming.',
                    'Learners will use different event blocks to start scripts in Scratch.',
                    'Learners will program a sprite to respond to key presses.',
                ],
                'notes': (
                    '<p>Programs often wait for something to happen before they act. Something that happens '
                    'and triggers code is called an <strong>event</strong>. Clicking, pressing a key or a '
                    'timer running out are all events. Your phone uses events too: tapping an app icon is an '
                    'event that opens the app.</p>'
                    '<p>In Scratch, the yellow <strong>Events</strong> blocks are "hat" blocks - they sit on '
                    'top of a script and start it:</p>'
                    '<ul><li><em>when green flag clicked</em> - starts when the program begins,</li>'
                    '<li><em>when [space] key pressed</em> - runs when a chosen key is pressed,</li>'
                    '<li><em>when this sprite clicked</em> - runs when you click the sprite,</li>'
                    '<li><em>when backdrop switches to ...</em> and <em>broadcast / when I receive</em> - '
                    'let sprites send messages to each other.</li></ul>'
                    '<p>One sprite can have <strong>several scripts</strong>, each started by a different event. '
                    'This is how games work: the right arrow key moves the player right, the left arrow key moves it left.</p>'
                    '<p>In Scratch, the stage uses <strong>x</strong> (left-right) and <strong>y</strong> '
                    '(up-down) coordinates. <em>change x by 10</em> moves right; <em>change y by 10</em> moves up.</p>'
                ),
                'key_terms': [
                    ('event', 'something that happens which makes code run, e.g. a click or key press'),
                    ('hat block', 'a block with a rounded top that starts a script'),
                    ('x and y', 'the coordinates of a sprite: x is left-right, y is up-down'),
                ],
                'example': {
                    'title': 'Guided activity: arrow-key controls',
                    'html': (
                        '<p>Build four short scripts for one sprite:</p>'
                        '<ul><li><em>when right arrow key pressed</em> -&gt; <em>change x by 10</em></li>'
                        '<li><em>when left arrow key pressed</em> -&gt; <em>change x by -10</em></li>'
                        '<li><em>when up arrow key pressed</em> -&gt; <em>change y by 10</em></li>'
                        '<li><em>when down arrow key pressed</em> -&gt; <em>change y by -10</em></li></ul>'
                        '<p>Add a fifth script: <em>when this sprite clicked</em> -&gt; <em>say "Ouch!" for 1 second</em>. '
                        'Test each event.</p>'
                    ),
                },
                'video': {'id': 'YQU4XMjdXHE', 'title': 'Scratch Tutorial - Events',
                          'channel': 'mrGcoding', 'minutes': 5},
                'worksheet': {
                    'instructions': 'Answer the questions about events and Scratch coordinates.',
                    'exercises': [
                        '1. What is an event in programming? Give two everyday examples.',
                        '2. Name three Scratch event blocks.',
                        '3. Why are event blocks called "hat" blocks?',
                        '4. Which block makes a sprite move left: change x by 10 or change x by -10?',
                        '5. Write the scripts needed to make a sprite move up and down with the arrow keys.',
                        '6. Can one sprite have more than one script? Explain with an example.',
                    ],
                },
                'quiz': [
                    ('mcq', 'Which of these is an event?', ['A key being pressed', 'A sprite\'s colour', 'The size of the stage'], 0),
                    ('mcq', 'In Scratch, "change y by 10" moves a sprite ...', ['left', 'right', 'up', 'down'], 2),
                    ('tf', 'A Scratch sprite can only have one script.', False),
                    ('tf', 'Event blocks in Scratch are yellow hat blocks that start scripts.', True),
                ],
                'homework': {
                    'title': 'Design a controller',
                    'instructions': 'Plan the controls for a simple game.',
                    'tasks': [
                        'Choose a game idea (e.g. a car avoiding potholes) and list the events needed.',
                        'For each event, write the Scratch blocks that should run.',
                    ],
                    'marks': 10,
                },
            },
            {
                'title': 'Loops: repeat, repeat, repeat',
                'minutes': 45,
                'objectives': [
                    'Learners will explain what a loop is and why programmers use loops.',
                    'Learners will use repeat and forever blocks in Scratch.',
                    'Learners will rewrite long sequences more efficiently with a loop.',
                ],
                'notes': (
                    '<p>A <strong>loop</strong> repeats a set of instructions. Instead of writing the same '
                    'blocks again and again, we put them inside a loop. Loops make code <strong>shorter</strong>, '
                    '<strong>easier to read</strong> and <strong>easier to change</strong>.</p>'
                    '<p>Scratch has orange <strong>Control</strong> blocks for loops:</p>'
                    '<ul><li><em>repeat (10)</em> - repeats the blocks inside a fixed number of times. This is '
                    'a <strong>count-controlled</strong> loop.</li>'
                    '<li><em>forever</em> - repeats the blocks until the program is stopped (e.g. background '
                    'music or a game that keeps checking for collisions).</li>'
                    '<li><em>repeat until &lt;condition&gt;</em> - repeats until something becomes true.</li></ul>'
                    '<p><strong>Example:</strong> To draw a square with the Pen extension you could write '
                    '"move 100, turn 90" four times (8 blocks). With a loop: <em>repeat 4: move 100, turn 90</em> '
                    '(3 blocks).</p>'
                    '<p>To find the number of repeats, look for the <strong>pattern</strong> that repeats in '
                    'the sequence. For a regular shape, the turn angle is 360 ÷ number of sides.</p>'
                ),
                'key_terms': [
                    ('loop', 'a set of instructions that is repeated'),
                    ('repeat block', 'a Scratch block that repeats the blocks inside a set number of times'),
                    ('forever block', 'a Scratch block that repeats until the program is stopped'),
                    ('pattern', 'something that repeats in a predictable way'),
                ],
                'example': {
                    'title': 'Worked example: drawing shapes with loops',
                    'html': (
                        '<p><strong>Square:</strong> 4 sides, turn 360 ÷ 4 = 90°.<br>'
                        '<em>pen down; repeat 4 { move 100 steps; turn right 90 degrees }</em></p>'
                        '<p><strong>Triangle:</strong> 3 sides, turn 360 ÷ 3 = 120°.<br>'
                        '<em>pen down; repeat 3 { move 100 steps; turn right 120 degrees }</em></p>'
                        '<p><strong>Walking animation:</strong> <em>forever { move 10 steps; next costume; wait 0.2 seconds; if on edge, bounce }</em></p>'
                    ),
                },
                'video': {'id': 'oWjiJIoG3nQ', 'title': 'Loops | Coding & Computer Science Song',
                          'channel': 'Scratch Garden', 'minutes': 3},
                'worksheet': {
                    'instructions': 'Answer the questions. Write Scratch blocks in words.',
                    'exercises': [
                        '1. What is a loop? Give two reasons why programmers use loops.',
                        '2. What is the difference between a repeat block and a forever block?',
                        '3. Rewrite with a loop: move 10, move 10, move 10, move 10, move 10.',
                        '4. Write a loop to draw a square with sides of 50 steps.',
                        '5. What angle must a sprite turn to draw a regular hexagon (6 sides)?',
                        '6. Write a loop that draws a regular hexagon.',
                        '7. Give one example of when a forever loop would be useful in a game.',
                    ],
                },
                'quiz': [
                    ('mcq', 'A set of instructions that is repeated is called a ...', ['bug', 'loop', 'sprite', 'backdrop'], 1),
                    ('mcq', 'To draw a square: repeat 4 { move 100; turn right ... degrees }',
                     ['45', '60', '90', '120'], 2),
                    ('tf', 'A forever block keeps repeating until the program is stopped.', True),
                    ('mcq', 'Which is the best way to make a sprite move 10 steps eight times?',
                     ['Eight separate "move 10" blocks', 'repeat 8 { move 10 steps }', 'move 10 steps once'], 1),
                ],
                'homework': {
                    'title': 'Loop patterns',
                    'instructions': 'Find loops in everyday life and in shapes.',
                    'tasks': [
                        'List three everyday activities that repeat (e.g. skipping rope, stirring a pot).',
                        'Write a loop algorithm for one of them.',
                        'Write Scratch loops to draw a regular pentagon (5 sides) - show how you worked out the angle.',
                    ],
                    'marks': 12,
                },
            },
            {
                'title': 'What is a robot? Input, process, output',
                'minutes': 45,
                'objectives': [
                    'Learners will define a robot and give examples of robots in daily life.',
                    'Learners will identify the input, process and output parts of a robot.',
                    'Learners will design a simple robot on paper to solve a problem.',
                ],
                'notes': (
                    '<p>A <strong>robot</strong> is a machine that can <strong>sense</strong> its surroundings, '
                    '<strong>think</strong> (follow a program) and <strong>act</strong> on its own. Robots are '
                    'used in car factories, in hospitals for surgery, in mines, on farms, to explore Mars and '
                    'even at home (robot vacuum cleaners).</p>'
                    '<p>Every robot works with three parts - <strong>input, process, output</strong>:</p>'
                    '<ul>'
                    '<li><strong>Input - sensors:</strong> collect information from the surroundings, like our '
                    'senses. Examples: light sensors, touch (bump) sensors, distance (ultrasonic) sensors, '
                    'cameras, microphones, temperature sensors.</li>'
                    '<li><strong>Process - controller:</strong> a small computer (microcontroller) runs the '
                    'program and decides what to do, like our brain.</li>'
                    '<li><strong>Output - actuators:</strong> parts that make the robot act. Examples: motors '
                    'that turn wheels or arms, lights (LEDs), speakers, screens.</li>'
                    '</ul>'
                    '<p>A robot also needs a <strong>power source</strong> (battery) and a '
                    '<strong>body/frame</strong>. Example: a robot vacuum uses a bump sensor (input); when it '
                    'bumps a wall the controller decides to turn (process); the motors turn the wheels (output).</p>'
                ),
                'key_terms': [
                    ('robot', 'a programmable machine that can sense, think and act'),
                    ('sensor', 'an input device that detects something in the surroundings'),
                    ('controller', 'the small computer that runs the robot\'s program'),
                    ('actuator', 'an output part, such as a motor, that makes the robot move or act'),
                ],
                'example': {
                    'title': 'Worked example: an automatic plant-watering robot',
                    'html': (
                        '<p><strong>Problem:</strong> plants in the school garden dry out over weekends.</p>'
                        '<ul><li><strong>Input:</strong> a soil-moisture sensor measures how wet the soil is.</li>'
                        '<li><strong>Process:</strong> the controller runs: <em>forever { if soil is dry then turn pump on, else turn pump off }</em>.</li>'
                        '<li><strong>Output:</strong> a small water pump (actuator) and a green LED that shows it is watering.</li>'
                        '<li><strong>Power:</strong> a battery charged by a small solar panel.</li></ul>'
                        '<p>Notice the loop from yesterday\'s lesson inside the robot\'s program!</p>'
                    ),
                },
                'video': {'id': '8wHJjLMnikU', 'title': 'Real-Life Robots',
                          'channel': 'SciShow Kids', 'minutes': 4},
                'worksheet': {
                    'instructions': 'Answer the questions in full sentences.',
                    'exercises': [
                        '1. What is a robot?',
                        '2. Name four places where robots are used.',
                        '3. Explain input, process and output in your own words.',
                        '4. Name three kinds of sensors and say what each detects.',
                        '5. Is a motor an input or an output? Explain.',
                        '6. A robot vacuum hits a chair. Describe its input, process and output.',
                        '7. Compare a robot with a person: which body parts are like sensors, controller and actuators?',
                    ],
                },
                'quiz': [
                    ('mcq', 'Which part of a robot collects information from the surroundings?',
                     ['Motor', 'Sensor', 'Battery', 'Wheel'], 1),
                    ('mcq', 'The controller in a robot is most like a person\'s ...', ['brain', 'hands', 'feet'], 0),
                    ('tf', 'A motor that turns a robot\'s wheels is an output (actuator).', True),
                    ('tf', 'A robot can work without any program.', False),
                    ('mcq', 'A distance sensor on a robot is an example of ...', ['output', 'power', 'input', 'frame'], 2),
                ],
                'homework': {
                    'title': 'Design a helper robot',
                    'instructions': 'Design a robot that solves a problem at home or in your community.',
                    'tasks': [
                        'Draw your robot and give it a name.',
                        'Label at least two sensors (inputs), the controller, and two actuators (outputs).',
                        'Write 3-5 sentences explaining what problem it solves and how it works.',
                    ],
                    'marks': 15,
                },
            },
        ],
    },
}
