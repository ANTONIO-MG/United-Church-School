"""core/seed_lessons/fet_core  —  Term 1, Week 1 demo lessons for the FET core subjects.

Offerings (12): Grades 10, 11 and 12 ×
    ENG-HL   English Home Language
    AFR-FAL  Afrikaans First Additional Language (Afrikaans Eerste Addisionele Taal)
    ZUL-FAL  isiZulu First Additional Language
    LO       Life Orientation

CAPS sources used
    * CAPS FET English Home Language Gr 10-12 (DBE, 2011) and the DBE / WCED FET Gr 10-12
      Annual Teaching Plans (ATP) for Term 1: listening and speaking, reading and viewing
      (literature: short story / novel, poetry, drama; comprehension and summary),
      writing and presenting (essays), language structures and conventions in context.
    * CAPS FET Afrikaans Eerste Addisionele Taal Gr 10-12 and the Term 1 ATP: luister en praat,
      lees en kyk (leesbegrip, kortverhaal, gedigte), skryf en aanbied (paragraaf, opstel,
      transaksionele tekste), taalstrukture en -konvensies (woordsoorte, tye, ontkenning).
    * CAPS FET isiZulu Ulimi Lokuqala Olwengeziwe Gr 10-12 and the Term 1 ATP: ukulalela
      nokukhuluma, ukufunda nokubuka (indaba emfushane, izinkondlo), ukubhala nokwethula
      (indima, incwadi), uhlelo lolimi (amabizo, izenzo).
    * CAPS FET Life Orientation Gr 10-12 and the Term 1 ATP, Topic 1 "Development of the self
      in society": Gr 10 self-awareness, self-esteem and self-development; Gr 11 plan and
      achieve life goals; Gr 12 life skills to adapt to change (stress and conflict management).

Week 1 = the first topic of each Term 1 ATP; Day 1-3 = 14, 15, 16 January 2026.
"""

LESSONS = {}

# ---------------------------------------------------------------------------
# ENGLISH HOME LANGUAGE
# ---------------------------------------------------------------------------

LESSONS[(10, 'ENG-HL')] = {
    'topic': 'Introduction to literature: elements of the short story and novel',
    'caps': "English HL Gr 10 Term 1 Weeks 1-2 (CAPS/ATP): Reading and viewing - intensive reading of "
            "a literary text (short story / novel: plot, character, setting, conflict, theme); reading "
            "comprehension strategies and summary; Writing - narrative essay (process writing); "
            "Language structures and conventions in context.",
    'summary': "Learners start the FET literature course by learning the building blocks of prose fiction, "
               "practise reading for meaning and summarising, and plan a narrative essay of their own.",
    'days': [
        {
            'title': 'The elements of fiction: plot, character, setting, conflict and theme',
            'minutes': 45,
            'objectives': [
                'Identify and define the main elements of a short story or novel.',
                'Describe the five stages of a conventional plot structure.',
                'Distinguish between internal and external conflict.',
            ],
            'notes': "<p>Every short story and novel you study in the FET Phase is built from the same "
                     "<strong>elements of fiction</strong>. Knowing these terms lets you talk and write about "
                     "literature precisely.</p>"
                     "<ul><li><strong>Plot</strong> - the sequence of events, usually arranged as "
                     "<em>exposition</em> (introduction of characters and setting), <em>rising action</em> "
                     "(complications build), <em>climax</em> (the turning point of greatest tension), "
                     "<em>falling action</em> and <em>resolution / denouement</em>.</li>"
                     "<li><strong>Character</strong> - the people (or beings) in the story. The "
                     "<em>protagonist</em> is the central character; the <em>antagonist</em> opposes them. "
                     "A <em>round</em> character is complex; a <em>flat</em> character has one or two traits. "
                     "A <em>dynamic</em> character changes; a <em>static</em> character does not.</li>"
                     "<li><strong>Setting</strong> - the time, place and social environment. Setting often "
                     "creates atmosphere and can reflect a character's situation.</li>"
                     "<li><strong>Conflict</strong> - the struggle that drives the plot. <em>External</em> "
                     "conflict is with another person, society or nature; <em>internal</em> conflict is a "
                     "struggle inside a character's mind.</li>"
                     "<li><strong>Theme</strong> - the central message or insight about life, expressed as a "
                     "statement (e.g. 'Greed destroys relationships'), not a single word.</li></ul>"
                     "<p>Also note the <strong>narrator</strong>: a first-person narrator uses 'I' and is part "
                     "of the story; a third-person narrator stands outside it and may be omniscient.</p>",
            'key_terms': [
                ('exposition', 'the opening part of a plot that introduces characters, setting and situation'),
                ('climax', 'the turning point of highest tension in the plot'),
                ('protagonist', 'the main character around whom the story is built'),
                ('antagonist', 'the character or force that opposes the protagonist'),
                ('theme', 'the central message or insight about life that a text conveys'),
            ],
            'example': {
                'title': 'Class activity: mapping a familiar story',
                'html': "<p>As a class, map the fable <em>The Tortoise and the Hare</em> onto the plot "
                        "structure:</p><ol><li><strong>Exposition:</strong> a boastful hare mocks a slow "
                        "tortoise; a race is arranged.</li><li><strong>Rising action:</strong> the hare races "
                        "ahead and decides to nap.</li><li><strong>Climax:</strong> the hare wakes to see the "
                        "tortoise near the finish line.</li><li><strong>Falling action:</strong> the hare "
                        "sprints but cannot catch up.</li><li><strong>Resolution:</strong> the tortoise "
                        "wins.</li></ol><p><strong>Conflict:</strong> external (hare vs tortoise) and internal "
                        "(the hare's arrogance). <strong>Theme:</strong> 'Steady effort can defeat careless "
                        "talent.'</p>",
            },
            'video': {'id': 'Zr1xLtSMMLo', 'title': 'The elements of a story | Reading | Khan Academy',
                      'channel': 'Khan Academy', 'minutes': 6},
            'worksheet': {
                'instructions': 'Answer in full sentences. Use a short story or novel you have read before.',
                'exercises': [
                    '1. Define "plot" and list its five stages in the correct order.',
                    '2. Explain the difference between a round and a flat character. Give an example of each.',
                    '3. What is the difference between internal and external conflict?',
                    '4. Name the protagonist and antagonist of a story you know and explain the conflict between them.',
                    '5. Describe the setting of that story (time, place, social environment) in 3-4 sentences.',
                    '6. Write the theme of that story as a full sentence, not a single word.',
                ],
            },
            'quiz': [
                ('mcq', 'Which stage of the plot is the turning point of greatest tension?',
                 ['Exposition', 'Rising action', 'Climax', 'Resolution'], 2),
                ('mcq', 'A character who changes significantly during a story is called a...',
                 ['dynamic character', 'static character', 'flat character', 'stock character'], 0),
                ('tf', "A character's struggle with his own fear is an example of internal conflict.", True),
                ('tf', 'A theme is best expressed as a single word, such as "love".', False),
            ],
            'homework': {
                'title': 'Elements of fiction in a film or series',
                'instructions': 'Choose a film or TV episode you know well and analyse it using the elements of fiction.',
                'tasks': [
                    'Draw a plot diagram and fill in the five stages.',
                    'Identify the protagonist and antagonist and describe one trait of each.',
                    'State the main conflict (internal or external) and the theme in one sentence each.',
                ],
                'marks': 15,
            },
        },
        {
            'title': 'Reading for meaning: comprehension strategies and summary',
            'minutes': 45,
            'objectives': [
                'Apply pre-reading, during-reading and post-reading strategies.',
                'Answer literal, inferential and evaluative comprehension questions.',
                'Summarise a passage in point form in my own words.',
            ],
            'notes': "<p>Comprehension is not only about finding answers; it is about <strong>making "
                     "meaning</strong>. Use a three-stage reading process:</p>"
                     "<ol><li><strong>Before reading:</strong> look at the title, headings and pictures and "
                     "predict the content.</li><li><strong>While reading:</strong> underline key ideas, "
                     "circle unfamiliar words and work out their meaning from context.</li>"
                     "<li><strong>After reading:</strong> state the main idea of each paragraph in a few "
                     "words.</li></ol>"
                     "<p>Questions test different levels:</p><ul><li><strong>Literal</strong> - the answer is "
                     "stated in the text.</li><li><strong>Inferential</strong> - you read between the lines "
                     "using clues.</li><li><strong>Evaluative / critical</strong> - you give and justify your "
                     "own opinion.</li></ul>"
                     "<p>Read the <em>mark allocation</em>: a 2-mark question needs two distinct points. "
                     "Answer in full sentences and use your own words unless asked to quote.</p>"
                     "<p><strong>Summary rules:</strong> select only main points, leave out examples, "
                     "repetition and figures of speech, write in your own words, and keep to the word limit "
                     "(state the word count at the end).</p>",
            'key_terms': [
                ('literal question', 'a question whose answer is directly stated in the text'),
                ('inferential question', 'a question that requires reading between the lines'),
                ('context clue', 'information near an unfamiliar word that helps you work out its meaning'),
                ('summary', 'a short version of a text that keeps only the main points, in your own words'),
            ],
            'example': {
                'title': 'Guided reading: a short passage',
                'html': "<p><em>Passage:</em> 'The taxi rank was a riot of noise long before sunrise. Hawkers "
                        "arranged pyramids of oranges while drivers shouted destinations. Thandi clutched her "
                        "new school bag, her stomach tight. Today she would start Grade 10 at a school where "
                        "she knew no one.'</p><ul><li><strong>Literal:</strong> What was Thandi carrying? - "
                        "A new school bag.</li><li><strong>Inferential:</strong> How did Thandi feel? Give a "
                        "reason. - She was nervous; her stomach was 'tight' and she knew no one at the school."
                        "</li><li><strong>Vocabulary in context:</strong> 'a riot of noise' suggests very loud, "
                        "chaotic sound.</li><li><strong>Summary point:</strong> Thandi feels anxious on her "
                        "first day at a new school.</li></ul>",
            },
            'video': {'id': 'n_vwvitBYqk', 'title': 'English 2020:  Summary', 'channel': 'Mindset', 'minutes': 25},
            'worksheet': {
                'instructions': "Read this passage, then answer the questions. 'Water is South Africa's most "
                                "precious resource. The country receives less rain than the world average, and "
                                "many dams fell to dangerously low levels during recent droughts. Households can "
                                "help by fixing leaking taps, taking shorter showers and reusing grey water in "
                                "the garden. Farmers, who use most of the country's water, are adopting drip "
                                "irrigation, which delivers water directly to plant roots.'",
                'exercises': [
                    '1. (Literal) According to the passage, who uses most of the country\'s water? (1)',
                    '2. (Literal) Name TWO ways households can save water. (2)',
                    '3. (Inferential) Why does the writer call water "precious"? (2)',
                    '4. (Vocabulary) Explain "grey water" using context clues. (1)',
                    '5. (Evaluative) Do you think individuals can make a real difference? Justify your answer. (2)',
                    '6. Summarise the passage in 3 points, in your own words (max 40 words). (3)',
                ],
            },
            'quiz': [
                ('mcq', 'A question that asks you to "read between the lines" is a/an...',
                 ['literal question', 'inferential question', 'spelling question', 'word-count question'], 1),
                ('mcq', 'Which of these should you LEAVE OUT of a summary?',
                 ['The main idea of each paragraph', 'Key facts', 'Examples and repetition', 'The central argument'], 2),
                ('tf', 'A 2-mark comprehension question usually needs two distinct points.', True),
                ('tf', 'In a summary you should copy the sentences of the passage word for word.', False),
            ],
            'homework': {
                'title': 'Summarise a news article',
                'instructions': 'Find a short news article (newspaper or a reputable news website) of about 250-400 words.',
                'tasks': [
                    'Underline or list the main idea of each paragraph.',
                    'Write a summary of 7 points in full sentences (max 90 words). Give the word count.',
                    'Write one literal and one inferential question about the article, with answers.',
                ],
                'marks': 15,
            },
        },
        {
            'title': 'Planning a narrative essay and using language in context',
            'minutes': 50,
            'objectives': [
                'Use the elements of fiction to plan a narrative essay.',
                'Follow the writing process: plan, draft, revise, edit, publish.',
                'Use the correct past tense and varied sentence types in narrative writing.',
            ],
            'notes': "<p>A <strong>narrative essay</strong> tells a story. In Grade 10 HL it should be "
                     "<strong>250-300 words</strong>, with a clear plot, convincing characters and a vivid "
                     "setting - the same elements you studied on Day 1.</p>"
                     "<p><strong>The writing process</strong></p><ol><li><strong>Plan:</strong> brainstorm or "
                     "mind-map; decide on narrator, conflict and climax.</li><li><strong>Draft:</strong> write "
                     "freely; do not worry about perfection.</li><li><strong>Revise:</strong> improve content "
                     "and structure - is the opening gripping? Does the climax build?</li>"
                     "<li><strong>Edit / proofread:</strong> correct spelling, punctuation and tense.</li>"
                     "<li><strong>Publish:</strong> write a neat final copy with a title.</li></ol>"
                     "<p><strong>Language in context</strong></p><ul><li>Keep to one tense (usually the "
                     "simple past: <em>walked, saw, ran</em>).</li><li>Vary sentences: a short sentence after "
                     "longer ones creates tension (<em>Then the lights went out.</em>).</li><li>Use direct "
                     "speech correctly: a new paragraph for each new speaker, inverted commas around the "
                     "spoken words.</li><li>Show, don't tell: instead of 'She was scared', write 'Her hands "
                     "trembled as she reached for the door.'</li></ul>",
            'key_terms': [
                ('narrative essay', 'an essay that tells a story with a plot, characters and setting'),
                ('first-person narrator', 'a narrator who tells the story as "I" and takes part in it'),
                ('direct speech', "the exact words a character says, placed in inverted commas"),
                ('show, don\'t tell', 'revealing feelings through actions and details rather than stating them'),
            ],
            'example': {
                'title': 'Worked example: from plan to opening paragraph',
                'html': "<p><strong>Topic:</strong> 'The day everything changed'.</p><p><strong>Plan:</strong> "
                        "narrator - first person; setting - a rural village during a storm; conflict - narrator "
                        "must cross a flooded river to fetch help for her grandmother; climax - she slips but "
                        "grabs a branch; resolution - she reaches the clinic and learns her own strength.</p>"
                        "<p><strong>Opening:</strong> 'The rain had not stopped for three days. I stood at the "
                        "edge of the river, watching brown water swallow the stepping stones one by one. Behind "
                        "me, in our small house, Gogo was coughing again.'</p><p>Notice: simple past tense, a "
                        "vivid setting, and the conflict is hinted at immediately.</p>",
            },
            'video': {'id': 'ltVHstQiBXo',
                      'title': 'how to write an excellent narrative essay. English Fal Paper 3.//Creative wring skills.',
                      'channel': 'Ms T.L.L Lechuti English (FAL&HL) lessons.', 'minutes': 12},
            'worksheet': {
                'instructions': 'Complete the planning and language exercises below.',
                'exercises': [
                    '1. Choose ONE topic: "Lost", "The stranger at the door" or "A promise kept". Write it down.',
                    '2. Draw a mind-map with narrator, setting, characters, conflict, climax and resolution.',
                    '3. Rewrite in the simple past tense: "She runs to the gate and sees that it is locked."',
                    '4. Punctuate as direct speech: where are you going asked Sipho',
                    '5. "Show, don\'t tell": rewrite "He was angry" as one descriptive sentence.',
                    '6. Write an opening paragraph (5-7 sentences) for your chosen topic.',
                ],
            },
            'quiz': [
                ('mcq', 'What is the recommended length of a Grade 10 HL narrative essay?',
                 ['80-100 words', '120-150 words', '250-300 words', '800-1000 words'], 2),
                ('mcq', 'Which step of the writing process focuses on correcting spelling and punctuation?',
                 ['Planning', 'Drafting', 'Editing / proofreading', 'Brainstorming'], 2),
                ('tf', 'When writing dialogue, you start a new paragraph for each new speaker.', True),
                ('mcq', 'Which sentence best "shows" rather than "tells"?',
                 ['She was very sad.', 'Tears slid down her cheeks as she folded the letter.',
                  'She felt sad that day.', 'Sadness was what she felt.'], 1),
            ],
            'homework': {
                'title': 'Narrative essay: first draft',
                'instructions': 'Use your plan from class to write the first draft of your narrative essay.',
                'tasks': [
                    'Write a draft of 250-300 words with a title.',
                    'Underline three "show, don\'t tell" sentences.',
                    'Check your tenses and direct speech punctuation before handing in.',
                ],
                'marks': 20,
            },
        },
    ],
}

LESSONS[(11, 'ENG-HL')] = {
    'topic': 'Poetry: figurative language and the analysis of a poem',
    'caps': "English HL Gr 11 Term 1 Weeks 1-2 (CAPS/ATP): Reading and viewing - poetry (figurative "
            "language, imagery, sound devices, tone, mood, theme; contextual questions); Writing - "
            "descriptive essay; Language structures and conventions in context (figurative language).",
    'summary': "Learners revise and extend their knowledge of figures of speech and sound devices, apply a "
               "step-by-step method to analyse a poem, and use imagery in a descriptive essay.",
    'days': [
        {
            'title': 'Figures of speech and sound devices',
            'minutes': 45,
            'objectives': [
                'Identify and explain simile, metaphor, personification, hyperbole and oxymoron.',
                'Identify sound devices such as alliteration, assonance and onomatopoeia.',
                'Explain the effect of a figure of speech, not just name it.',
            ],
            'notes': "<p>Poets compress meaning into few words. <strong>Figurative language</strong> helps them "
                     "do this by creating vivid images and unexpected connections.</p>"
                     "<ul><li><strong>Simile</strong> - a comparison using <em>like</em> or <em>as</em>: "
                     "'The city sparkled like a jewel box.'</li><li><strong>Metaphor</strong> - a direct "
                     "comparison stating one thing <em>is</em> another: 'Time is a thief.'</li>"
                     "<li><strong>Personification</strong> - giving human qualities to non-human things: "
                     "'The wind howled its grief.'</li><li><strong>Hyperbole</strong> - deliberate "
                     "exaggeration: 'I have told you a million times.'</li><li><strong>Oxymoron</strong> - two "
                     "contradictory words side by side: 'deafening silence'.</li></ul>"
                     "<p><strong>Sound devices</strong>: <em>alliteration</em> (repeated initial consonants: "
                     "'silent, silver sea'), <em>assonance</em> (repeated vowel sounds: 'the light of the fire "
                     "is high'), <em>onomatopoeia</em> (words that imitate sounds: 'buzz', 'crackle'), and "
                     "<em>rhyme</em> and <em>rhythm</em>.</p>"
                     "<p>In an exam you earn marks for the <strong>effect</strong>. Use the formula: "
                     "<strong>name the device + quote + explain what it suggests and why it works</strong>.</p>",
            'key_terms': [
                ('metaphor', 'a direct comparison that says one thing is another'),
                ('personification', 'giving human qualities to an object, animal or idea'),
                ('oxymoron', 'two contradictory words placed together, e.g. "bitter sweet"'),
                ('assonance', 'repetition of vowel sounds in nearby words'),
                ('onomatopoeia', 'a word that imitates the sound it describes'),
            ],
            'example': {
                'title': 'Worked example: naming and explaining a device',
                'html': "<p><strong>Line:</strong> 'The old house groaned beneath the weight of years.'</p>"
                        "<p><strong>Device:</strong> personification - the house 'groaned' like a tired person."
                        "</p><p><strong>Effect:</strong> the house seems exhausted and burdened, which "
                        "emphasises its age and decay and creates a sad, heavy mood.</p><p><strong>Line:</strong> "
                        "'Hope is a candle in a storm.'</p><p><strong>Device:</strong> metaphor. "
                        "<strong>Effect:</strong> hope is shown as small and fragile but still giving light in "
                        "danger - it may be extinguished, yet it guides us.</p>",
            },
            'video': {'id': 'JwhouCNq-Fc', 'title': 'What makes a poem … a poem? - Melissa Kovacs',
                      'channel': 'TED-Ed', 'minutes': 5},
            'worksheet': {
                'instructions': 'Identify the figure of speech or sound device in each line, then explain its effect.',
                'exercises': [
                    '1. "Her voice was music to his ears."',
                    '2. "The leaves danced in the autumn breeze."',
                    '3. "He ran as fast as a cheetah."',
                    '4. "Peter Piper picked a peck of pickled peppers."',
                    '5. "The bees buzzed lazily in the heat."',
                    '6. "I am so hungry I could eat a horse."',
                    '7. "It was an open secret."',
                ],
            },
            'quiz': [
                ('mcq', '"The classroom was a zoo." This is an example of...',
                 ['simile', 'metaphor', 'onomatopoeia', 'alliteration'], 1),
                ('mcq', 'Which line contains an oxymoron?',
                 ['The sun smiled down on us.', 'A deafening silence filled the hall.',
                  'The kettle hissed.', 'She is as brave as a lion.'], 1),
                ('tf', 'Alliteration is the repetition of initial consonant sounds in nearby words.', True),
                ('mcq', '"The thunder grumbled in the distance." The device is...',
                 ['hyperbole', 'simile', 'personification', 'oxymoron'], 2),
                ('tf', 'In an exam, naming a figure of speech is enough to earn full marks.', False),
            ],
            'homework': {
                'title': 'Figurative language hunt',
                'instructions': 'Find examples of figurative language in song lyrics, advertisements or poems.',
                'tasks': [
                    'Find and write down five examples, each a different device.',
                    'For each, name the device and explain its effect in one or two sentences.',
                ],
                'marks': 10,
            },
        },
        {
            'title': 'How to analyse a poem: a step-by-step method',
            'minutes': 50,
            'objectives': [
                'Use a structured method to analyse an unseen poem.',
                'Describe the tone and mood of a poem and support it with quotations.',
                'Answer contextual questions on a poem in full sentences.',
            ],
            'notes': "<p>When you meet a poem for the first time, use a clear method so you do not feel lost."
                     "</p><ol><li><strong>Title:</strong> what does it suggest? Re-check it at the end.</li>"
                     "<li><strong>First reading:</strong> read the whole poem aloud. What is it about on the "
                     "surface (the literal meaning)?</li><li><strong>Speaker and situation:</strong> who is "
                     "speaking, to whom, and where?</li><li><strong>Structure:</strong> stanzas, line length, "
                     "rhyme scheme (label rhymes a, b, c...), enjambment and punctuation.</li>"
                     "<li><strong>Diction and imagery:</strong> which words stand out? Which figures of speech "
                     "are used?</li><li><strong>Tone and mood:</strong> <em>tone</em> is the speaker's attitude "
                     "(bitter, nostalgic, mocking); <em>mood</em> is the feeling created in the reader.</li>"
                     "<li><strong>Theme:</strong> what insight about life does the poem offer?</li></ol>"
                     "<p><strong>Enjambment</strong> is when a sentence runs over into the next line without a "
                     "pause; it can create flow or suspense. A <strong>caesura</strong> is a pause in the "
                     "middle of a line.</p><p>Always support your points with short quotations.</p>",
            'key_terms': [
                ('tone', "the speaker's attitude towards the subject"),
                ('mood', 'the atmosphere or feeling a poem creates in the reader'),
                ('enjambment', 'a sentence running on from one line of poetry into the next'),
                ('rhyme scheme', 'the pattern of rhymes at line endings, labelled with letters'),
                ('diction', "the writer's choice of words"),
            ],
            'example': {
                'title': 'Guided analysis: a short poem',
                'html': "<p><em>Dawn Market</em> (a short poem for class analysis)<br>Before the sun has "
                        "washed its face,<br>the women build their towers of fruit;<br>the street, still "
                        "grey, begins to race<br>with hooting taxis, boots on boots.</p><ul><li><strong>Literal:"
                        "</strong> a street market being set up before sunrise.</li><li><strong>Rhyme scheme:"
                        "</strong> abab (face/race, fruit/boots - a half-rhyme).</li><li><strong>Personification:"
                        "</strong> the sun 'washed its face' - it is like a person waking up, so the day feels "
                        "fresh and new.</li><li><strong>Metaphor:</strong> 'towers of fruit' shows how carefully "
                        "and high the fruit is stacked.</li><li><strong>Tone:</strong> admiring; "
                        "<strong>mood:</strong> energetic and busy.</li></ul>",
            },
            'video': {'id': 'lqyRnxhfA64', 'title': 'How to Analyse a Poem in 3 Minutes', 'channel': 'Jeddle',
                      'minutes': 4},
            'worksheet': {
                'instructions': "Read the poem and answer the questions. 'The Old Tree': The old tree stands "
                                "where the roads divide, / its arms held wide to the burning sky; / it has watched "
                                "a hundred summers die / and still it will not step aside.",
                'exercises': [
                    '1. What is the literal situation described in the poem? (1)',
                    '2. Identify the rhyme scheme of the stanza. (1)',
                    '3. Identify the figure of speech in "its arms held wide" and explain its effect. (2)',
                    '4. What does "watched a hundred summers die" suggest about the tree? (2)',
                    '5. Describe the tone of the last line. Quote to support your answer. (2)',
                    '6. Suggest a possible theme for the poem. (2)',
                ],
            },
            'quiz': [
                ('mcq', "The speaker's attitude towards the subject of a poem is called the...",
                 ['mood', 'tone', 'rhyme', 'stanza'], 1),
                ('tf', 'Enjambment is when a sentence continues from one line into the next without a pause.', True),
                ('mcq', 'A poem whose lines end "day, night, way, light" has the rhyme scheme...',
                 ['aabb', 'abba', 'abab', 'abcd'], 2),
                ('tf', 'Mood is the feeling a poem creates in the reader.', True),
            ],
            'homework': {
                'title': 'Analyse a poem of your choice',
                'instructions': 'Choose a short poem (8-16 lines) from your anthology or a library book.',
                'tasks': [
                    'Write down the title, poet and literal meaning in two sentences.',
                    'Identify the rhyme scheme and two figures of speech, explaining their effect.',
                    'Describe the tone and mood, and state the theme in one sentence.',
                ],
                'marks': 15,
            },
        },
        {
            'title': 'Descriptive essay: painting pictures with words',
            'minutes': 50,
            'objectives': [
                'Explain the features of a descriptive essay.',
                'Use sensory imagery and figurative language in my own writing.',
                'Plan and draft a descriptive paragraph using a logical structure.',
            ],
            'notes': "<p>A <strong>descriptive essay</strong> creates a vivid picture of a person, place, "
                     "object or experience. Unlike a narrative, it does not need a strong plot; its power lies "
                     "in <strong>detail</strong>. A Grade 11 HL essay is about <strong>350-400 words</strong>."
                     "</p><p><strong>Features</strong></p><ul><li><strong>Sensory imagery:</strong> appeal to "
                     "all five senses - sight, sound, smell, taste and touch.</li><li><strong>Figurative "
                     "language:</strong> use the similes, metaphors and personification from Day 1 - but "
                     "sparingly and originally (avoid cliches like 'as white as snow').</li>"
                     "<li><strong>Precise diction:</strong> choose exact nouns and strong verbs ('the dog "
                     "<em>slunk</em>' rather than 'the dog <em>walked slowly</em>').</li><li><strong>Logical "
                     "structure:</strong> organise by space (near to far, left to right), time (dawn to dusk) "
                     "or importance.</li><li><strong>A dominant impression:</strong> every detail should build "
                     "one overall feeling (peaceful, chaotic, eerie).</li></ul>"
                     "<p>The poem analysis skills you practised yesterday help here: think like a poet about "
                     "every word.</p>",
            'key_terms': [
                ('descriptive essay', 'an essay that creates a vivid picture through detailed description'),
                ('sensory imagery', 'description that appeals to sight, sound, smell, taste or touch'),
                ('dominant impression', 'the single overall feeling a description creates'),
                ('cliche', 'an overused expression that has lost its impact'),
            ],
            'example': {
                'title': 'Worked example: improving a description',
                'html': "<p><strong>Weak:</strong> 'The beach was nice. There were lots of people and it was "
                        "hot.'</p><p><strong>Improved:</strong> 'By noon the sand burned the soles of my feet. "
                        "Umbrellas bloomed like giant flowers along the shore, and the air was thick with "
                        "sunscreen and the salty tang of the sea. Somewhere a radio crackled, competing with "
                        "the hush and roar of the waves.'</p><p>Senses used: touch (burned), sight (umbrellas), "
                        "smell (sunscreen, salt), sound (radio, waves). Devices: simile ('like giant flowers'), "
                        "onomatopoeia ('crackled', 'hush'). Dominant impression: a hot, crowded, lively day.</p>",
            },
            'video': {'id': 'RSoRzTtwgP4', 'title': 'How to write descriptively - Nalo Hopkinson',
                      'channel': 'TED-Ed', 'minutes': 5},
            'worksheet': {
                'instructions': 'Complete the exercises to build your descriptive writing skills.',
                'exercises': [
                    '1. List one detail for each of the five senses for the topic "A busy taxi rank".',
                    '2. Replace the weak verb with a stronger one: "The car went down the road."',
                    '3. Rewrite the cliche "as cold as ice" as an original simile.',
                    '4. Write one sentence using personification to describe a storm.',
                    '5. Choose a dominant impression (e.g. peaceful, eerie) for the topic "My bedroom at midnight".',
                    '6. Write a descriptive paragraph (8-10 sentences) on one of the topics above.',
                ],
            },
            'quiz': [
                ('mcq', 'What is the main focus of a descriptive essay?',
                 ['A strong plot with a climax', 'Vivid detail that creates a picture',
                  'Arguing for one side of an issue', 'Giving instructions'], 1),
                ('tf', 'A good descriptive essay appeals to more than one of the five senses.', True),
                ('mcq', 'Which verb is the most precise and vivid?',
                 ['went', 'moved', 'staggered', 'did'], 2),
                ('tf', 'Cliches such as "as busy as a bee" make descriptive writing more original.', False),
            ],
            'homework': {
                'title': 'Descriptive essay draft',
                'instructions': 'Write a first draft of a descriptive essay titled "A place I will never forget".',
                'tasks': [
                    'Make a sensory mind-map before you write.',
                    'Write a draft of 350-400 words with a clear dominant impression.',
                    'Highlight at least three figures of speech you used.',
                ],
                'marks': 20,
            },
        },
    ],
}

LESSONS[(12, 'ENG-HL')] = {
    'topic': 'Drama, comprehension and summary, and the argumentative essay',
    'caps': "English HL Gr 12 Term 1 Weeks 1-2 (CAPS/ATP): Reading and viewing - introduction to the "
            "prescribed drama (elements of drama); comprehension and summary writing (Paper 1); Writing - "
            "argumentative / discursive essay (Paper 3); Language structures and conventions in context.",
    'summary': "Matric learners are introduced to the conventions of drama for their prescribed play, sharpen "
               "Paper 1 comprehension and summary technique, and plan an argumentative essay.",
    'days': [
        {
            'title': 'Introduction to drama: the elements and conventions of a play',
            'minutes': 50,
            'objectives': [
                'Explain the elements and conventions of drama.',
                'Distinguish between dialogue, monologue, soliloquy, aside and stage directions.',
                'Explain dramatic irony and its effect on an audience.',
            ],
            'notes': "<p>A play is written to be <strong>performed</strong>, so it is read differently from a "
                     "novel. There is usually no narrator: we learn about characters through what they say "
                     "and do, and what others say about them.</p>"
                     "<ul><li><strong>Acts and scenes</strong> divide the action (Shakespeare's tragedies have "
                     "five acts).</li><li><strong>Dialogue</strong> - conversation between characters; it "
                     "drives the plot and reveals character.</li><li><strong>Monologue</strong> - a long speech "
                     "by one character to others on stage.</li><li><strong>Soliloquy</strong> - a character, "
                     "alone on stage, speaks thoughts aloud so the audience learns their true feelings.</li>"
                     "<li><strong>Aside</strong> - a short remark to the audience that other characters on "
                     "stage do not hear.</li><li><strong>Stage directions</strong> - italic instructions about "
                     "movement, tone, setting and props.</li></ul>"
                     "<p><strong>Dramatic irony</strong> occurs when the audience knows something a character "
                     "does not. It builds suspense and tension. In <strong>tragedy</strong>, the "
                     "<em>tragic hero</em> is a person of high status whose <em>tragic flaw</em> (e.g. "
                     "ambition, jealousy, indecision) leads to downfall.</p>"
                     "<p>In Paper 2 you will answer contextual questions on an extract and write a literary "
                     "essay, so start a character and theme log for your prescribed play now.</p>",
            'key_terms': [
                ('soliloquy', 'a speech in which a character alone on stage reveals inner thoughts'),
                ('aside', 'a short remark to the audience, unheard by other characters'),
                ('dramatic irony', 'when the audience knows something a character does not'),
                ('tragic flaw', "a weakness in the hero's character that leads to downfall"),
                ('stage directions', 'instructions in a script about action, tone, setting or props'),
            ],
            'example': {
                'title': 'Class activity: reading a short scene',
                'html': "<p>Read aloud in pairs:</p><p><em>(A kitchen. LINDA wipes the table. JAMES enters, "
                        "hiding a letter behind his back.)</em><br>LINDA: You're late again.<br>JAMES: "
                        "<em>(smiling too widely)</em> Traffic.<br><em>(Aside)</em> If she finds this letter, "
                        "everything is over.</p><ul><li>Stage directions show James is hiding something and is "
                        "nervous ('smiling too widely').</li><li>The <strong>aside</strong> tells the audience "
                        "his secret, which Linda cannot hear.</li><li>This creates <strong>dramatic irony</strong>"
                        " and suspense: we wait to see if Linda discovers the letter.</li></ul>",
            },
            'video': {'id': 'y2f726TyGNM', 'title': 'The Elements of Drama - Ms. Murphy', 'channel': 'Megan Murphy',
                      'minutes': 8},
            'worksheet': {
                'instructions': 'Answer the questions in full sentences.',
                'exercises': [
                    '1. Why is there usually no narrator in a play? How do we learn about characters instead?',
                    '2. Explain the difference between a monologue and a soliloquy.',
                    '3. What is the purpose of stage directions? Give two examples of what they may indicate.',
                    '4. Define dramatic irony and explain why playwrights use it.',
                    '5. What is a tragic flaw? Give an example from any play or film you know.',
                    '6. Write a 6-line scene of your own that includes one aside and two stage directions.',
                ],
            },
            'quiz': [
                ('mcq', 'A character alone on stage speaking his thoughts aloud is delivering a...',
                 ['dialogue', 'soliloquy', 'stage direction', 'chorus'], 1),
                ('tf', 'In an aside, the other characters on stage hear what is said.', False),
                ('mcq', 'When the audience knows something a character does not, this is called...',
                 ['verbal irony', 'situational irony', 'dramatic irony', 'satire'], 2),
                ('mcq', 'A tragic hero\'s downfall is usually caused by a...',
                 ['tragic flaw', 'happy ending', 'subplot', 'stage direction'], 0),
            ],
            'homework': {
                'title': 'Start a drama log',
                'instructions': 'Begin a log for your prescribed play (or a play you know if you do not have it yet).',
                'tasks': [
                    'List the main characters with two character traits each.',
                    'Describe the setting (time and place) and the main conflict.',
                    'Find or invent one example of dramatic irony and explain its effect.',
                ],
                'marks': 15,
            },
        },
        {
            'title': 'Paper 1 skills: comprehension and the summary',
            'minutes': 50,
            'objectives': [
                'Answer comprehension questions at different cognitive levels using the mark allocation.',
                'Follow the matric summary rules (7 points, 90 words, own words).',
                'Distinguish between main points and supporting detail.',
            ],
            'notes': "<p>Paper 1 tests your ability to read critically. In the <strong>comprehension</strong>, "
                     "questions range from literal recall to evaluation. Tips:</p>"
                     "<ul><li>Read the questions before the second reading so you read with purpose.</li>"
                     "<li>Note the <strong>command word</strong>: <em>identify</em> (name), <em>explain</em> "
                     "(give reasons), <em>discuss</em> (examine more than one aspect), <em>critically "
                     "comment</em> (give and justify an opinion).</li><li>Use the <strong>mark allocation</strong>"
                     ": 3 marks usually means three clear points.</li><li>Answer in your own words unless asked "
                     "to <em>quote</em>; then use inverted commas and quote exactly.</li></ul>"
                     "<p><strong>Summary (10 marks)</strong>: you are usually asked for <strong>seven points</"
                     "strong> in fluent sentences of <strong>no more than 90 words</strong>, or in point form."
                     "</p><ol><li>Read the instruction carefully - summarise only what is asked.</li><li>Select "
                     "seven relevant main points.</li><li>Leave out examples, statistics, quotations and "
                     "descriptions.</li><li>Rephrase in your own words.</li><li>Check the word count and state "
                     "it at the end, e.g. (86 words).</li></ol>",
            'key_terms': [
                ('command word', 'the verb in a question that tells you what to do, e.g. "explain"'),
                ('critically comment', 'give a reasoned opinion supported by evidence from the text'),
                ('main point', 'a key idea that is essential to the meaning of the text'),
                ('supporting detail', 'examples, statistics or descriptions that illustrate a main point'),
            ],
            'example': {
                'title': 'Worked example: selecting summary points',
                'html': "<p><em>Text extract:</em> 'Sleep is essential for teenagers. During deep sleep the "
                        "brain stores new information, which is why students who sleep eight to ten hours "
                        "remember more. For example, one study found that well-rested learners scored 20% "
                        "higher on memory tests. Lack of sleep also weakens the immune system and affects "
                        "mood.'</p><p><strong>Instruction:</strong> summarise the benefits of sleep.</p>"
                        "<ul><li>Point 1: Sleep helps the brain store and remember information.</li>"
                        "<li>Point 2: Enough sleep strengthens the body's resistance to illness.</li>"
                        "<li>Point 3: Sleep helps keep moods stable.</li></ul><p>Left out: the 20% statistic "
                        "(example) and 'eight to ten hours' (detail).</p>",
            },
            'video': {'id': 'v15t9uUP0HM', 'title': 'how to ace summary writing. English Fal paper 1.',
                      'channel': 'Ms T.L.L Lechuti English (FAL&HL) lessons.', 'minutes': 12},
            'worksheet': {
                'instructions': "Read the passage and answer. 'Cellphones have changed how young people learn. "
                                "Learners can look up information instantly, join study groups on messaging "
                                "apps and watch video lessons. However, constant notifications break "
                                "concentration, and many learners use their phones late at night, losing sleep. "
                                "Experts suggest switching phones off during homework and charging them outside "
                                "the bedroom.'",
                'exercises': [
                    '1. Identify TWO ways cellphones help learners. (2)',
                    '2. Explain how notifications affect learning. (2)',
                    '3. Quote the phrase that shows phones may harm health. (1)',
                    '4. Critically comment: should cellphones be allowed in classrooms? (3)',
                    '5. Write a summary of the advantages and disadvantages in 5 points (max 60 words). (5)',
                    '6. State the word count of your summary.',
                ],
            },
            'quiz': [
                ('mcq', 'How many points and words are usually required in a matric summary?',
                 ['3 points, 50 words', '7 points, 90 words', '10 points, 200 words', '5 points, 150 words'], 1),
                ('tf', 'Statistics and examples should usually be left out of a summary.', True),
                ('mcq', 'The command word "critically comment" asks you to...',
                 ['copy a sentence from the text', 'name one thing', 'give and justify your opinion',
                  'count the words'], 2),
                ('tf', 'When asked to "quote", you may change the words of the text slightly.', False),
            ],
            'homework': {
                'title': 'Summary practice',
                'instructions': 'Use an editorial or feature article of 400-600 words from a newspaper or magazine.',
                'tasks': [
                    'Write down the summary instruction you set yourself (e.g. "the causes of...").',
                    'Write a seven-point summary in fluent sentences of no more than 90 words.',
                    'Write two inferential questions on the article with model answers.',
                ],
                'marks': 15,
            },
        },
        {
            'title': 'The argumentative essay: planning a convincing argument',
            'minutes': 50,
            'objectives': [
                'Distinguish between an argumentative and a discursive essay.',
                'Plan an essay with a clear thesis, supporting arguments and a counter-argument.',
                'Use formal register, linking words and persuasive techniques correctly.',
            ],
            'notes': "<p>In an <strong>argumentative essay</strong> you take <strong>one side</strong> of an "
                     "issue and convince the reader. In a <strong>discursive essay</strong> you present both "
                     "sides fairly before reaching a balanced conclusion. A Grade 12 HL essay is "
                     "<strong>400-450 words</strong>.</p>"
                     "<p><strong>Structure</strong></p><ol><li><strong>Introduction</strong> - hook the reader "
                     "and state your <em>thesis</em> (your position) clearly.</li><li><strong>Body paragraphs"
                     "</strong> - one argument per paragraph: topic sentence, explanation, evidence (fact, "
                     "example, expert opinion), link back to the thesis.</li><li><strong>Counter-argument and "
                     "rebuttal</strong> - acknowledge the opposing view, then show why it is weaker.</li>"
                     "<li><strong>Conclusion</strong> - restate the thesis in new words and end with a "
                     "strong final thought or call to action.</li></ol>"
                     "<p><strong>Language in context</strong>: use a formal register (no slang or "
                     "contractions), linking words (<em>furthermore, however, consequently, on the other "
                     "hand</em>) and persuasive techniques such as rhetorical questions and the rule of three. "
                     "Avoid emotive exaggeration that weakens credibility.</p>",
            'key_terms': [
                ('thesis', 'the main position or claim that an essay argues'),
                ('counter-argument', 'an opposing view that the writer acknowledges'),
                ('rebuttal', 'the reasoning that shows why the counter-argument is weaker'),
                ('discursive essay', 'an essay that presents both sides of an issue in a balanced way'),
                ('register', 'the level of formality of language'),
            ],
            'example': {
                'title': 'Worked example: an essay plan',
                'html': "<p><strong>Topic:</strong> 'School uniforms should be abolished.' (Position: disagree)"
                        "</p><ul><li><strong>Thesis:</strong> School uniforms should remain because they promote "
                        "equality, discipline and school identity.</li><li><strong>Argument 1:</strong> "
                        "uniforms reduce visible differences between rich and poor learners.</li>"
                        "<li><strong>Argument 2:</strong> they create a focused, disciplined learning "
                        "environment.</li><li><strong>Argument 3:</strong> they build pride and a sense of "
                        "belonging.</li><li><strong>Counter-argument:</strong> uniforms limit self-expression. "
                        "<strong>Rebuttal:</strong> learners can express themselves through ideas, talents and "
                        "activities rather than clothing.</li><li><strong>Conclusion:</strong> call on schools "
                        "to keep affordable, practical uniforms.</li></ul>",
            },
            'video': {'id': 'VZKUeEBryOk', 'title': 'How to Write an Argumentative Essay with Example',
                      'channel': 'Literacy In Focus', 'minutes': 8},
            'worksheet': {
                'instructions': 'Plan an argumentative essay and practise the language features.',
                'exercises': [
                    '1. Choose a topic: "Social media does more harm than good" OR "Matric exams should be abolished".',
                    '2. Write your thesis statement in one sentence.',
                    '3. List three arguments with one piece of evidence each.',
                    '4. Write one counter-argument and your rebuttal.',
                    '5. Rewrite in formal register: "Kids today can\'t live without their phones, it\'s crazy."',
                    '6. Use "however", "furthermore" and "consequently" correctly in three sentences on your topic.',
                ],
            },
            'quiz': [
                ('mcq', 'What is the main difference between an argumentative and a discursive essay?',
                 ['A discursive essay presents both sides; an argumentative essay takes one side',
                  'An argumentative essay has no conclusion', 'A discursive essay must be informal',
                  'There is no difference'], 0),
                ('tf', 'Including a counter-argument and rebuttal can make an argument more convincing.', True),
                ('mcq', 'Which linking word introduces a contrasting idea?',
                 ['furthermore', 'consequently', 'however', 'firstly'], 2),
                ('tf', 'Slang and contractions are appropriate in a formal argumentative essay.', False),
            ],
            'homework': {
                'title': 'Argumentative essay: introduction and one body paragraph',
                'instructions': 'Using your plan from class, write the opening sections of your essay.',
                'tasks': [
                    'Write an introduction with a hook and a clear thesis.',
                    'Write one full body paragraph (topic sentence, explanation, evidence, link).',
                    'Underline the linking words you used.',
                ],
                'marks': 15,
            },
        },
    ],
}

# ---------------------------------------------------------------------------
# AFRIKAANS EERSTE ADDISIONELE TAAL (AFR-FAL)
# ---------------------------------------------------------------------------

LESSONS[(10, 'AFR-FAL')] = {
    'topic': "Luister en praat: begroeting en gesprek; woordsoorte; skryf 'n paragraaf",
    'caps': "Afrikaans EAT Gr 10 Kwartaal 1 Weke 1-2 (CAPS/ATP): Luister en praat - begroeting, "
            "voorstelling en gesprekvoering; Taalstrukture en -konvensies - woordsoorte in konteks; "
            "Skryf en aanbied - 'n paragraaf / kort beskrywende teks oor jouself (skryfproses).",
    'summary': "Learners greet, introduce themselves and hold a short conversation in Afrikaans, revise the "
               "parts of speech (woordsoorte), and write a well-structured paragraph about themselves.",
    'days': [
        {
            'title': 'Begroeting en voorstelling: greetings and a first conversation',
            'minutes': 40,
            'objectives': [
                'Ek kan iemand in Afrikaans groet en myself voorstel (greet and introduce myself).',
                "Ek kan 'n kort gesprek voer met vrae en antwoorde (hold a short conversation).",
                "Ek weet wanneer om 'jy' en wanneer om 'u' te gebruik (informal vs respectful 'you').",
            ],
            'notes': "<p>In Afrikaans we greet according to the time of day. Use these phrases to start a "
                     "conversation:</p>"
                     "<ul><li><strong>Goeiemôre</strong> - Good morning; <strong>Goeiemiddag</strong> - Good "
                     "afternoon; <strong>Goeienaand</strong> - Good evening</li>"
                     "<li><strong>Hallo! / Haai!</strong> - Hello! / Hi! (informal)</li>"
                     "<li><strong>Hoe gaan dit met jou?</strong> - How are you?<br><em>Dit gaan goed, "
                     "dankie. En met jou?</em> - I'm well, thank you. And you?</li>"
                     "<li><strong>Wat is jou naam?</strong> - What is your name?<br><em>My naam is ...</em></li>"
                     "<li><strong>Hoe oud is jy?</strong> - <em>Ek is vyftien jaar oud.</em></li>"
                     "<li><strong>Waar woon jy?</strong> - <em>Ek woon in Durban.</em></li>"
                     "<li><strong>Aangename kennis.</strong> - Pleased to meet you.</li>"
                     "<li><strong>Totsiens! / Sien jou môre!</strong> - Goodbye! / See you tomorrow!</li></ul>"
                     "<p><strong>Jy or u?</strong> Use <em>jy/jou</em> with friends and people your age. Use "
                     "<em>u</em> to show respect to adults and teachers: <em>Hoe gaan dit met u, Meneer?</em></p>"
                     "<p><strong>Klaskamertaal</strong> (classroom language): <em>Mag ek asseblief iets vra?</em> "
                     "(May I please ask something?), <em>Ek verstaan nie.</em> (I don't understand.), "
                     "<em>Kan u dit asseblief herhaal?</em> (Can you please repeat it?)</p>",
            'key_terms': [
                ('Goeiemôre', 'Good morning'),
                ('Hoe gaan dit met jou?', 'How are you?'),
                ('Aangename kennis', 'Pleased to meet you'),
                ('u', 'the respectful form of "you", used for adults and teachers'),
                ('Totsiens', 'Goodbye'),
            ],
            'example': {
                'title': "Gesprek: 'n nuwe leerder (role-play in pairs)",
                'html': "<p><strong>Lerato:</strong> Goeiemôre! My naam is Lerato. Wat is jou naam?<br>"
                        "<strong>Pieter:</strong> Goeiemôre, Lerato. Ek is Pieter. Aangename kennis.<br>"
                        "<strong>Lerato:</strong> Aangename kennis. Hoe gaan dit met jou?<br>"
                        "<strong>Pieter:</strong> Dit gaan goed, dankie. En met jou?<br>"
                        "<strong>Lerato:</strong> Baie goed, dankie. In watter graad is jy?<br>"
                        "<strong>Pieter:</strong> Ek is in graad 10. Ek is nuut by die skool.<br>"
                        "<strong>Lerato:</strong> Welkom! Kom, ek wys jou waar ons klas is.<br>"
                        "<strong>Pieter:</strong> Baie dankie!</p><p>Practise the dialogue, then change the "
                        "names, grade and details to make it your own.</p>",
            },
            'video': {'id': 'fvLtNRondyU', 'title': 'Learn Afrikaans for Beginners | Greetings | Groete | Lesson 1',
                      'channel': 'Learn Afrikaans', 'minutes': 8},
            'worksheet': {
                'instructions': 'Beantwoord die vrae in volsinne in Afrikaans. (Answer in full Afrikaans sentences.)',
                'exercises': [
                    '1. Wat is jou naam?',
                    '2. Hoe oud is jy?',
                    '3. Waar woon jy?',
                    '4. In watter graad is jy?',
                    '5. How do you greet your teacher at 8 o\'clock in the morning? Write the greeting in Afrikaans.',
                    '6. Translate: "Pleased to meet you. How are you, Sir?"',
                    '7. Write a short dialogue (6 lines) in which you meet a new learner.',
                ],
            },
            'quiz': [
                ('mcq', 'Which greeting would you use at 7 p.m.?',
                 ['Goeiemôre', 'Goeiemiddag', 'Goeienaand', 'Totsiens'], 2),
                ('mcq', 'What does "Aangename kennis" mean?',
                 ['Goodbye', 'Pleased to meet you', 'Thank you very much', 'See you tomorrow'], 1),
                ('tf', 'You should use "u" to speak respectfully to a teacher.', True),
                ('mcq', 'Someone asks "Hoe gaan dit met jou?" Which is the best answer?',
                 ['My naam is Sipho.', 'Ek woon in Kaapstad.', 'Dit gaan goed, dankie.', 'Ek is vyftien.'], 2),
            ],
            'homework': {
                'title': 'Stel jouself voor (introduce yourself)',
                'instructions': 'Prepare a short oral introduction of yourself in Afrikaans to present in class.',
                'tasks': [
                    'Write 6-8 sentences: name, age, where you live, grade, family and one hobby.',
                    'Practise saying it aloud three times (record yourself if you can).',
                    'Learn the three time-of-day greetings by heart.',
                ],
                'marks': 10,
            },
        },
        {
            'title': 'Woordsoorte: the parts of speech in Afrikaans',
            'minutes': 45,
            'objectives': [
                'Ek kan die belangrikste woordsoorte noem en verduidelik.',
                "Ek kan woordsoorte in 'n sin identifiseer.",
                'Ek kan die regte lidwoord en voornaamwoord gebruik.',
            ],
            'notes': "<p>Every word in a sentence belongs to a <strong>woordsoort</strong> (part of speech). "
                     "Knowing them helps you build correct sentences and answer language questions.</p>"
                     "<ul><li><strong>Selfstandige naamwoord</strong> (noun): <em>seun, skool, Kaapstad, "
                     "liefde</em></li><li><strong>Werkwoord</strong> (verb): <em>loop, eet, skryf, is</em></li>"
                     "<li><strong>Byvoeglike naamwoord</strong> (adjective): <em>mooi, groot, slim</em> - "
                     "describes a noun</li><li><strong>Bywoord</strong> (adverb): <em>vinnig, gister, hier</em> "
                     "- tells how, when or where</li><li><strong>Voornaamwoord</strong> (pronoun): <em>ek, jy, "
                     "hy, sy, ons, julle, hulle</em></li><li><strong>Lidwoord</strong> (article): <em>die</em> "
                     "(the) and <em>'n</em> (a/an)</li><li><strong>Voorsetsel</strong> (preposition): <em>op, "
                     "in, onder, by, met</em></li><li><strong>Voegwoord</strong> (conjunction): <em>en, maar, "
                     "want, omdat</em></li><li><strong>Telwoord</strong> (numeral): <em>een, twee, eerste</em>"
                     "</li><li><strong>Tussenwerpsel</strong> (interjection): <em>Eina! Sjoe! Ag!</em></li></ul>"
                     "<p>Note: Afrikaans has only one definite article, <em>die</em>, for all nouns - "
                     "<em>die man, die vrou, die boek</em>. Proper nouns (names of people and places) start "
                     "with a capital letter.</p>",
            'key_terms': [
                ('selfstandige naamwoord', 'noun - the name of a person, place, thing or idea'),
                ('werkwoord', 'verb - an action or state'),
                ('byvoeglike naamwoord', 'adjective - describes a noun'),
                ('bywoord', 'adverb - says how, when or where something happens'),
                ('voegwoord', 'conjunction - joins words or sentences'),
            ],
            'example': {
                'title': "Uitgewerkte voorbeeld: ontleed 'n sin (analyse a sentence)",
                'html': "<p><strong>Sin:</strong> <em>Die slim seun lees vinnig 'n boek in die klas.</em></p>"
                        "<ul><li><strong>Die</strong> - lidwoord</li><li><strong>slim</strong> - byvoeglike "
                        "naamwoord</li><li><strong>seun</strong> - selfstandige naamwoord</li>"
                        "<li><strong>lees</strong> - werkwoord</li><li><strong>vinnig</strong> - bywoord "
                        "(how?)</li><li><strong>'n</strong> - lidwoord</li><li><strong>boek</strong> - "
                        "selfstandige naamwoord</li><li><strong>in</strong> - voorsetsel</li><li><strong>die"
                        "</strong> - lidwoord</li><li><strong>klas</strong> - selfstandige naamwoord</li></ul>"
                        "<p>Translation: The clever boy reads a book quickly in the class.</p>",
            },
            'video': {'id': 'IdoNDOsxj4w', 'title': 'Woordsoorte Les 1: Oorsig', 'channel': 'Skribbelskrywer',
                      'minutes': 8},
            'worksheet': {
                'instructions': 'Identifiseer die onderstreepte (aangeduide) woordsoort. Name the part of speech of the word in brackets.',
                'exercises': [
                    "1. Die [hond] blaf hard.",
                    "2. Ons [speel] sokker na skool.",
                    "3. Sy dra 'n [rooi] rok.",
                    "4. Hy hardloop [vinnig] huis toe.",
                    "5. Die boek lê [op] die tafel.",
                    "6. Ek is moeg, [maar] ek werk nog.",
                    "7. [Hulle] woon in Bloemfontein.",
                    "8. Write your own sentence with a noun, a verb, an adjective and a preposition. Label them.",
                ],
            },
            'quiz': [
                ('mcq', "Which woordsoort is 'vinnig' in: 'Hy hardloop vinnig'?",
                 ['selfstandige naamwoord', 'bywoord', 'lidwoord', 'voegwoord'], 1),
                ('mcq', 'Which word is a voorsetsel (preposition)?', ['onder', 'mooi', 'skryf', 'hulle'], 0),
                ('tf', "'Die' and ''n' are lidwoorde (articles).", True),
                ('mcq', 'Which word is a byvoeglike naamwoord (adjective)?', ['eet', 'groot', 'en', 'gister'], 1),
                ('tf', "'Omdat' is a werkwoord (verb).", False),
            ],
            'homework': {
                'title': 'Woordsoorte in my wêreld',
                'instructions': 'Find Afrikaans words around you (packaging, signs, a magazine or the textbook).',
                'tasks': [
                    'Write down 10 Afrikaans words and the woordsoort of each.',
                    'Write three sentences of your own and label every word in one of them.',
                ],
                'marks': 10,
            },
        },
        {
            'title': "Skryf 'n paragraaf: writing about myself with correct word order",
            'minutes': 45,
            'objectives': [
                "Ek kan 'n paragraaf met 'n kernsin, ondersteunende sinne en 'n slotsin skryf.",
                'Ek kan die korrekte Afrikaanse woordorde (STOMPI) gebruik.',
                "Ek kan sinne met 'en', 'maar', 'want' en 'omdat' verbind.",
            ],
            'notes': "<p>A good <strong>paragraaf</strong> has one main idea:</p>"
                     "<ul><li><strong>Kernsin</strong> (topic sentence) - introduces the main idea.</li>"
                     "<li><strong>Ondersteunende sinne</strong> (supporting sentences) - give details and "
                     "examples.</li><li><strong>Slotsin</strong> (concluding sentence) - rounds off the idea."
                     "</li></ul>"
                     "<p><strong>Woordorde - STOMPI</strong>: in a simple Afrikaans sentence the order is "
                     "<strong>S</strong>ubject - <strong>T</strong>(verb) - <strong>T</strong>ime - "
                     "<strong>O</strong>bject - <strong>M</strong>anner - <strong>P</strong>lace - "
                     "<strong>I</strong>nfinitive. Example: <em>Ek ry elke dag met die bus skool toe.</em> "
                     "(S: Ek, V: ry, T: elke dag, M: met die bus, P: skool toe).</p>"
                     "<p>If you start with a time word, the verb comes <strong>second</strong>: <em>Elke dag ry "
                     "ek met die bus skool toe.</em></p>"
                     "<p><strong>Voegwoorde</strong>: <em>en, maar, want</em> keep the normal word order: "
                     "<em>Ek hou van Wiskunde, want dit is interessant.</em> <em>Omdat</em> sends the verb to "
                     "the end: <em>Ek hou van Wiskunde, omdat dit interessant <strong>is</strong>.</em></p>"
                     "<p>Use the writing process: plan, write a draft, check spelling and word order, then "
                     "write a neat final copy.</p>",
            'key_terms': [
                ('kernsin', 'topic sentence'),
                ('slotsin', 'concluding sentence'),
                ('woordorde', 'word order'),
                ('omdat', 'because - sends the verb to the end of the clause'),
            ],
            'example': {
                'title': "Voorbeeldparagraaf: 'Ek en my lewe'",
                'html': "<p><em>My naam is Lerato Mokoena en ek is vyftien jaar oud. Ek woon saam met my ma en "
                        "twee broers in Soweto. Ek is in graad 10 en my gunstelingvak is Wiskunde, want ek hou "
                        "van probleme oplos. Na skool speel ek netbal en luister ek na musiek. Eendag wil ek "
                        "'n ingenieur word, omdat ek graag brûe wil bou. Ek is 'n vriendelike en hardwerkende "
                        "mens.</em></p><ul><li>Kernsin: the first sentence introduces Lerato.</li><li>Notice "
                        "inversion: <em>Na skool <strong>speel</strong> ek</em>.</li><li>Notice <em>omdat</em>: "
                        "the verb <em>bou</em> moves to the end.</li></ul>",
            },
            'video': {'id': 'aGSu1jJZ-10', 'title': 'Verhalende Opstel (Narrative Essay) | Afrikaans',
                      'channel': 'Goon School', 'minutes': 10},
            'worksheet': {
                'instructions': 'Voltooi die oefeninge. (Complete the exercises.)',
                'exercises': [
                    '1. Put the words in the correct order: skool toe / ek / elke oggend / loop',
                    '2. Begin the sentence with "Môre": Ek speel môre sokker.',
                    '3. Join with "want": Ek is moeg. Ek het laat geslaap.',
                    '4. Join with "omdat": Sy is gelukkig. Sy het die toets geslaag.',
                    '5. Write a kernsin for a paragraph about your family.',
                    '6. Write a paragraph of 8-10 sentences titled "Ek en my lewe".',
                ],
            },
            'quiz': [
                ('mcq', 'Which sentence has the correct word order?',
                 ['Ek skool toe loop elke dag.', 'Ek loop elke dag skool toe.',
                  'Elke dag ek loop skool toe.', 'Loop ek skool toe elke dag.'], 1),
                ('tf', "After 'omdat' the verb moves to the end of the clause.", True),
                ('mcq', 'What is a "slotsin"?',
                 ['a topic sentence', 'a concluding sentence', 'a question', 'a title'], 1),
                ('mcq', "Complete: 'Gister ___ ek na die winkel gegaan.'", ['het', 'is', 'sal', 'was'], 0),
            ],
            'homework': {
                'title': "Paragraaf: 'My gunstelingplek'",
                'instructions': 'Write a paragraph in Afrikaans about your favourite place.',
                'tasks': [
                    'Write 8-10 sentences with a kernsin, supporting sentences and a slotsin.',
                    "Use at least one sentence with 'want' and one with 'omdat'.",
                    'Start one sentence with a time word and check the inversion.',
                ],
                'marks': 15,
            },
        },
    ],
}

LESSONS[(11, 'AFR-FAL')] = {
    'topic': "Lees en kyk: die kortverhaal; tye (teenwoordige, verlede, toekomende tyd); die informele brief",
    'caps': "Afrikaans EAT Gr 11 Kwartaal 1 Weke 1-2 (CAPS/ATP): Lees en kyk - leesbegrip en die "
            "kortverhaal (intrige, karakters, ruimte, konflik, tema); Taalstrukture en -konvensies - tye; "
            "Skryf en aanbied - langer transaksionele teks: die informele (vriendskaplike) brief.",
    'summary': "Learners read and analyse a short story using the literary elements, practise the three tenses "
               "in context, and write a friendly letter about their first school week.",
    'days': [
        {
            'title': 'Die kortverhaal: elements of a short story',
            'minutes': 45,
            'objectives': [
                'Ek kan die elemente van \'n kortverhaal noem en verduidelik.',
                "Ek kan die intrige (plot) van 'n kort teks in fases verdeel.",
                'Ek kan innerlike en uiterlike konflik onderskei.',
            ],
            'notes': "<p>A <strong>kortverhaal</strong> (short story) is a short prose text with only a few "
                     "characters and one main event. Learn these terms in Afrikaans:</p>"
                     "<ul><li><strong>Intrige / storielyn</strong> (plot): <em>inleiding</em> (introduction), "
                     "<em>verwikkeling</em> (complication), <em>klimaks / hoogtepunt</em> (climax), "
                     "<em>ontknoping</em> (resolution) and <em>slot</em> (ending).</li>"
                     "<li><strong>Karakters</strong>: the <em>hoofkarakter / protagonis</em> (main character), "
                     "the <em>antagonis</em> (opponent) and <em>byfigure</em> (minor characters).</li>"
                     "<li><strong>Ruimte</strong> (setting): where and when the story takes place.</li>"
                     "<li><strong>Konflik</strong>: <em>innerlike konflik</em> (inside a character's mind) or "
                     "<em>uiterlike konflik</em> (with another person, society or nature).</li>"
                     "<li><strong>Tema</strong>: the main message of the story.</li>"
                     "<li><strong>Verteller</strong>: an <em>ek-verteller</em> (first person) or a "
                     "<em>derdepersoonsverteller</em> (third person).</li></ul>",
            'key_terms': [
                ('intrige', 'plot - the sequence of events'),
                ('hoofkarakter', 'main character / protagonist'),
                ('ruimte', 'setting - time and place'),
                ('innerlike konflik', 'internal conflict'),
                ('tema', 'theme - the main message'),
            ],
            'example': {
                'title': "Lees saam: 'Die spaarblik' ('n kort teks)",
                'html': "<p><em>Sipho spaar al maande lank geld vir 'n nuwe fiets. Elke Saterdag werk hy in "
                        "die winkel op die hoek. Een middag sien hy sy jonger broer, Themba, huil. Themba se "
                        "skoene is stukkend en hy skaam hom om so skool toe te gaan. Sipho kyk na sy spaarblik "
                        "en dink lank na. Die volgende oggend koop hy vir Themba nuwe skoene. Sy fiets sal moet "
                        "wag, maar Themba se glimlag is vir hom meer werd.</em></p><ul><li><strong>Hoofkarakter:"
                        "</strong> Sipho - hardwerkend en liefdevol.</li><li><strong>Ruimte:</strong> 'n dorp; "
                        "die winkel en die huis.</li><li><strong>Konflik:</strong> innerlik - Sipho moet kies "
                        "tussen sy fiets en sy broer.</li><li><strong>Klimaks:</strong> Sipho kyk na sy "
                        "spaarblik en besluit.</li><li><strong>Tema:</strong> Liefde vir jou familie is meer "
                        "werd as besittings.</li></ul>",
            },
            'video': {'id': 'KBnkNKaFdLQ', 'title': "Wat is 'n kortverhaal?", 'channel': 'Juffrou', 'minutes': 6},
            'worksheet': {
                'instructions': "Gebruik die teks 'Die spaarblik'. Beantwoord in volsinne.",
                'exercises': [
                    '1. Wie is die hoofkarakter?',
                    '2. Waarvoor spaar Sipho geld?',
                    '3. Waarom huil Themba?',
                    '4. Is die konflik innerlik of uiterlik? Verduidelik.',
                    '5. Wat is die klimaks van die verhaal?',
                    '6. Is die verteller \'n ek-verteller of \'n derdepersoonsverteller? Hoe weet jy?',
                    '7. Wat is die tema van die verhaal? Skryf dit in een sin.',
                ],
            },
            'quiz': [
                ('mcq', "What is the 'klimaks' of a story?",
                 ['the introduction', 'the turning point / highest point of tension', 'the title', 'the ending'], 1),
                ('mcq', "'Ruimte' in a short story refers to the...", ['theme', 'characters', 'setting', 'narrator'], 2),
                ('tf', 'Innerlike konflik takes place inside a character\'s mind.', True),
                ('tf', "An 'ek-verteller' tells the story in the third person (hy/sy).", False),
            ],
            'homework': {
                'title': 'Ontleed \'n kortverhaal',
                'instructions': 'Read a short story in Afrikaans from your textbook or anthology.',
                'tasks': [
                    'Name the hoofkarakter and describe him/her with two adjectives in Afrikaans.',
                    'Describe the ruimte (time and place).',
                    'Identify the konflik and state the tema in one Afrikaans sentence.',
                ],
                'marks': 10,
            },
        },
        {
            'title': 'Tye: teenwoordige, verlede en toekomende tyd',
            'minutes': 45,
            'objectives': [
                'Ek kan sinne in die teenwoordige, verlede en toekomende tyd skryf.',
                'Ek ken die uitsonderings in die verlede tyd (is, het, kan, wil, moet).',
                "Ek weet wanneer 'n werkwoord nie 'ge-' kry nie.",
            ],
            'notes': "<p>Afrikaans tenses are simple - verbs do not change for <em>ek, jy, hy</em> etc.</p>"
                     "<ul><li><strong>Teenwoordige tyd</strong> (present): <em>Ek lees 'n boek.</em></li>"
                     "<li><strong>Verlede tyd</strong> (past): <strong>het</strong> + <strong>ge-</strong>verb "
                     "at the end: <em>Ek het 'n boek gelees.</em></li><li><strong>Toekomende tyd</strong> "
                     "(future): <strong>sal</strong> + verb at the end: <em>Ek sal 'n boek lees.</em></li></ul>"
                     "<p><strong>Uitsonderings</strong> (exceptions) in the past tense:</p><ul><li>is - "
                     "<em>was</em>: <em>Hy is siek. - Hy was siek.</em></li><li>het - <em>het gehad</em>: "
                     "<em>Ek het 'n hond. - Ek het 'n hond gehad.</em></li><li>kan - <em>kon</em>, wil - "
                     "<em>wou</em>, moet - <em>moes</em>, sal - <em>sou</em>: <em>Ek wil swem. - Ek wou swem."
                     "</em></li></ul>"
                     "<p><strong>No ge-</strong> for verbs that begin with the unstressed prefixes <em>be-, "
                     "ge-, her-, er-, ont-, ver-</em>: <em>Ek verstaan. - Ek het verstaan.</em> <em>Hy betaal. "
                     "- Hy het betaal.</em></p><p><strong>Separable verbs</strong> join together: <em>Ek maak "
                     "die deur oop. - Ek het die deur oopgemaak.</em></p>",
            'key_terms': [
                ('teenwoordige tyd', 'present tense'),
                ('verlede tyd', 'past tense (het + ge-)'),
                ('toekomende tyd', 'future tense (sal)'),
                ('skeibare werkwoord', 'separable verb, e.g. oopmaak, opstaan'),
            ],
            'example': {
                'title': "Uitgewerkte voorbeeld: skryf 'Die spaarblik' in die verlede tyd",
                'html': "<ul><li><em>Sipho spaar geld.</em> - <strong>Sipho het geld gespaar.</strong></li>"
                        "<li><em>Elke Saterdag werk hy in die winkel.</em> - <strong>Elke Saterdag het hy in die "
                        "winkel gewerk.</strong></li><li><em>Themba se skoene is stukkend.</em> - "
                        "<strong>Themba se skoene was stukkend.</strong></li><li><em>Hy koop nuwe skoene.</em> - "
                        "<strong>Hy het nuwe skoene gekoop.</strong></li><li>Future: <strong>Hy sal nuwe skoene "
                        "koop.</strong></li></ul><p>Notice that after a time phrase (<em>Elke Saterdag</em>) the "
                        "verb <em>het</em> stays in second position.</p>",
            },
            'video': {'id': 'yeMyv4e63dc', 'title': 'Verlede tyd (The past tense) | Afrikaans FAL',
                      'channel': 'Bad Teacher', 'minutes': 8},
            'worksheet': {
                'instructions': 'Skryf die sinne oor in die tyd tussen hakies. (Rewrite in the tense in brackets.)',
                'exercises': [
                    "1. Ons eet pap vir ontbyt. (verlede tyd)",
                    "2. Die meisie is baie gelukkig. (verlede tyd)",
                    "3. Ek kan nie kom nie. (verlede tyd)",
                    "4. Hy verkoop sy ou fiets. (verlede tyd)",
                    "5. Ma maak die venster oop. (verlede tyd)",
                    "6. Hulle speel Saterdag sokker. (toekomende tyd)",
                    "7. Ek het my huiswerk gedoen. (teenwoordige tyd)",
                ],
            },
            'quiz': [
                ('mcq', "Past tense of 'Ek skryf 'n brief':",
                 ["Ek het 'n brief geskryf.", "Ek sal 'n brief skryf.", "Ek het 'n brief skryf.",
                  "Ek skryf 'n brief gehad."], 0),
                ('mcq', "Past tense of 'Sy is moeg':", ['Sy het moeg.', 'Sy was moeg.', 'Sy sal moeg wees.',
                                                       'Sy het moeg gewees.'], 1),
                ('tf', "'Verstaan' does not take ge- in the past tense: 'Ek het verstaan.'", True),
                ('mcq', "Future tense of 'Ons gaan see toe':",
                 ['Ons het see toe gegaan.', 'Ons gaan see toe gehad.', 'Ons sal see toe gaan.',
                  'Ons was see toe.'], 2),
            ],
            'homework': {
                'title': 'My vakansie in drie tye',
                'instructions': 'Write about your holiday and your plans for the year.',
                'tasks': [
                    'Write five sentences in the verlede tyd about what you did in the holidays.',
                    'Write three sentences in the teenwoordige tyd about your school day now.',
                    'Write three sentences in the toekomende tyd about your goals for this year.',
                ],
                'marks': 11,
            },
        },
        {
            'title': "Die informele brief: writing to a friend",
            'minutes': 45,
            'objectives': [
                "Ek ken die formaat van 'n informele (vriendskaplike) brief.",
                "Ek kan 'n brief van 120-150 woorde aan 'n vriend skryf.",
                'Ek gebruik die verlede en toekomende tyd korrek in my brief.',
            ],
            'notes': "<p>An <strong>informele brief</strong> (friendly letter) is written to a friend or family "
                     "member. The tone is relaxed, but the format must be correct.</p>"
                     "<ol><li><strong>Adres van die skrywer</strong> - top right-hand corner.</li>"
                     "<li><strong>Datum</strong> - under the address, e.g. <em>16 Januarie 2026</em>.</li>"
                     "<li><strong>Aanhef</strong> (greeting) - on the left: <em>Liewe Johan,</em> or "
                     "<em>Liewe Ouma,</em></li><li><strong>Inleiding</strong> - ask how the person is: "
                     "<em>Hoe gaan dit met jou? Ek hoop jy is gesond.</em></li><li><strong>Liggaam</strong> "
                     "(body) - two or three paragraphs with your news.</li><li><strong>Slot</strong> - end "
                     "warmly: <em>Skryf gou terug!</em></li><li><strong>Groete</strong> - <em>Groete / Baie "
                     "liefde,</em> then <em>Jou vriend / Jou vriendin</em> and your first name.</li></ol>"
                     "<p>Use the tenses you practised: the <em>verlede tyd</em> for what happened, the "
                     "<em>toekomende tyd</em> for plans. Use <em>jy/jou</em> (informal), not <em>u</em>.</p>",
            'key_terms': [
                ('aanhef', 'the greeting at the start of a letter, e.g. "Liewe ..."'),
                ('liggaam', 'the body of the letter'),
                ('slot', 'the closing paragraph'),
                ('Jou vriendin', 'Your friend (female); Jou vriend (male)'),
            ],
            'example': {
                'title': "Voorbeeldbrief (liggaam)",
                'html': "<p><em>Liewe Johan,</em></p><p><em>Hoe gaan dit met jou? Ek hoop jy het 'n lekker "
                        "vakansie gehad.</em></p><p><em>Ek het hierdie week in graad 11 begin. Ons het 'n nuwe "
                        "Afrikaans-onderwyser en sy is baie vriendelik. Op Woensdag het ons 'n kortverhaal "
                        "gelees oor 'n seun wat vir sy broer skoene koop. Ek het dit baie geniet.</em></p>"
                        "<p><em>Volgende week sal ons vir die sokkerspan oefen. Ek hoop ek word gekies!</em></p>"
                        "<p><em>Skryf gou terug en vertel my van jou nuwe skool.</em></p><p><em>Groete<br>Jou "
                        "vriend<br>Sipho</em></p>",
            },
            'video': {'id': 'mvgOpUo3OY8', 'title': 'Vriendskaplike Brief (Friendly Letter) | Afrikaans',
                      'channel': 'Goon School', 'minutes': 8},
            'worksheet': {
                'instructions': 'Beplan en skryf jou brief. (Plan and write your letter.)',
                'exercises': [
                    '1. Where do you write the writer\'s address and the date?',
                    '2. Write a correct aanhef for a letter to your grandmother.',
                    '3. Write two opening sentences asking how your friend is.',
                    '4. Write three sentences in the verlede tyd about your first school week.',
                    '5. Write two sentences in the toekomende tyd about your plans.',
                    '6. Write a correct ending (slot and groete) for a letter to a friend.',
                ],
            },
            'quiz': [
                ('mcq', 'Where is the writer\'s address placed in an informal letter?',
                 ['bottom left', 'top right', 'in the middle', 'it is left out'], 1),
                ('mcq', 'Which is a suitable aanhef for a friendly letter?',
                 ['Geagte Meneer,', 'Liewe Thandi,', 'Insake:', 'Die uwe,'], 1),
                ('tf', "In a letter to a friend you should use 'u' instead of 'jy'.", False),
                ('tf', "'Jou vriendin' can be used to end a friendly letter.", True),
            ],
            'homework': {
                'title': 'Skryf \'n informele brief',
                'instructions': 'Write a friendly letter (120-150 words) to a friend at another school about your first week in Grade 11.',
                'tasks': [
                    'Use the correct format: address, date, aanhef, inleiding, liggaam, slot, groete.',
                    'Use at least three sentences in the verlede tyd and two in the toekomende tyd.',
                    'Check your spelling and word order before you hand in.',
                ],
                'marks': 20,
            },
        },
    ],
}

LESSONS[(12, 'AFR-FAL')] = {
    'topic': 'Lees en kyk: gedigte en beeldspraak; ontkenning; die formele brief',
    'caps': "Afrikaans EAT Gr 12 Kwartaal 1 Weke 1-2 (CAPS/ATP): Lees en kyk - poesie (beeldspraak, "
            "klankeffekte, tema, toon); Taalstrukture en -konvensies - die ontkennende vorm; Skryf en "
            "aanbied - langer transaksionele teks: die formele brief.",
    'summary': "Matric learners analyse imagery and sound in a poem, master the Afrikaans negative form "
               "(dubbele nie), and write a formal letter in the correct format and register.",
    'days': [
        {
            'title': "Gedigte: beeldspraak en klankeffekte",
            'minutes': 45,
            'objectives': [
                'Ek kan vergelyking, metafoor, personifikasie en hiperbool identifiseer.',
                'Ek kan alliterasie, assonansie en herhaling in \'n gedig raaksien.',
                'Ek kan die effek van beeldspraak in eenvoudige Afrikaans of Engels verduidelik.',
            ],
            'notes': "<p><strong>Beeldspraak</strong> (figurative language) helps a poet create pictures in "
                     "the reader's mind.</p>"
                     "<ul><li><strong>Vergelyking</strong> (simile) - uses <em>soos</em> or <em>so ... soos"
                     "</em>: <em>Sy is so mooi soos 'n roos.</em></li><li><strong>Metafoor</strong> (metaphor) "
                     "- says one thing <em>is</em> another: <em>Hy is 'n leeu op die veld.</em></li>"
                     "<li><strong>Personifikasie</strong> - gives human qualities to things: <em>Die wind "
                     "fluister deur die bome.</em></li><li><strong>Hiperbool</strong> (hyperbole) - "
                     "exaggeration: <em>Ek het dit al 'n miljoen keer gesê!</em></li></ul>"
                     "<p><strong>Klankeffekte</strong> (sound effects):</p><ul><li><strong>Alliterasie</strong> "
                     "- repeated consonants at the start of words: <em>die wilde wind waai</em>.</li>"
                     "<li><strong>Assonansie</strong> - repeated vowel sounds: <em>die maan staan kaal en vaal</em>.</li>"
                     "<li><strong>Herhaling</strong> (repetition) - emphasises an idea or feeling.</li>"
                     "<li><strong>Rym</strong> (rhyme) at the end of lines.</li></ul>"
                     "<p>In the exam, name the device, quote it and explain its <strong>effek</strong> "
                     "(what it makes you see or feel).</p>",
            'key_terms': [
                ('vergelyking', 'simile (uses "soos")'),
                ('metafoor', 'metaphor'),
                ('personifikasie', 'personification'),
                ('alliterasie', 'alliteration'),
                ('herhaling', 'repetition'),
            ],
            'example': {
                'title': "Ontleed saam: 'Somermiddag' ('n kort gedig vir die klas)",
                'html': "<p><em>Die son is 'n vuurbal bo die dorp,<br>die strate lê en hyg soos 'n hond.<br>"
                        "'n Windjie fluister in die bloekomboom,<br>en ek droom, en ek droom, en ek droom.</em>"
                        "</p><ul><li><strong>Metafoor:</strong> 'Die son is 'n vuurbal' - the sun is so hot it "
                        "seems like a ball of fire.</li><li><strong>Personifikasie en vergelyking:</strong> 'die "
                        "strate lê en hyg soos 'n hond' - the streets 'pant' like a tired dog, showing the "
                        "terrible heat.</li><li><strong>Personifikasie:</strong> 'n windjie 'fluister' - a soft, "
                        "gentle breeze.</li><li><strong>Herhaling:</strong> 'en ek droom' - creates a slow, "
                        "sleepy rhythm.</li><li><strong>Stemming</strong> (mood): lazy, hot and dreamy.</li></ul>",
            },
            'video': {'id': 'TyHTbbcI52c', 'title': 'Beeldspraak 1, 2 en 3: metafoor, vergelyking, personifikasie',
                      'channel': 'Learning Afrikaans', 'minutes': 8},
            'worksheet': {
                'instructions': 'Identifiseer die beeldspraak of klankeffek en verduidelik die effek.',
                'exercises': [
                    "1. Die son lag vir ons.",
                    "2. My broer is so sterk soos 'n os.",
                    "3. Die klaskamer is 'n bynes.",
                    "4. Ek is so honger, ek kan 'n hele bees eet!",
                    "5. Die blou berge bly bo.",
                    "6. Reën, reën, reën - die hele dag lank.",
                    "7. Write your own metafoor about school.",
                ],
            },
            'quiz': [
                ('mcq', "'Hy is so vinnig soos 'n jagluiperd.' This is a...",
                 ['metafoor', 'vergelyking', 'personifikasie', 'alliterasie'], 1),
                ('mcq', "'Die wind huil om die huis.' This is...",
                 ['personifikasie', 'hiperbool', 'vergelyking', 'rym'], 0),
                ('tf', "'Die klaskamer is 'n dieretuin' is an example of a metafoor.", True),
                ('mcq', "Repeated consonant sounds at the start of words is called...",
                 ['assonansie', 'herhaling', 'alliterasie', 'hiperbool'], 2),
            ],
            'homework': {
                'title': 'Beeldspraak in liedjies of gedigte',
                'instructions': 'Find an Afrikaans song or poem (textbook, radio, internet).',
                'tasks': [
                    'Write down four lines that contain beeldspraak.',
                    'Name the device in each line and explain its effect in one sentence.',
                    'Write a short poem of four lines with one vergelyking and one personifikasie.',
                ],
                'marks': 12,
            },
        },
        {
            'title': 'Ontkenning: the negative form (dubbele nie)',
            'minutes': 45,
            'objectives': [
                'Ek kan sinne korrek ontken met die dubbele nie.',
                'Ek kan positiewe woorde verander na hul negatiewe vorm (iemand - niemand).',
                'Ek weet wanneer net een nie gebruik word.',
            ],
            'notes': "<p>Afrikaans uses a <strong>double negative</strong> (<em>dubbele nie</em>). The first "
                     "<em>nie</em> comes after the verb (or after the object pronoun), and the second "
                     "<em>nie</em> comes at the end of the sentence.</p>"
                     "<ul><li><em>Ek eet vleis.</em> - <strong>Ek eet nie vleis nie.</strong></li>"
                     "<li><em>Hy het die boek gelees.</em> - <strong>Hy het nie die boek gelees nie.</strong>"
                     "</li><li><em>Sy kan swem.</em> - <strong>Sy kan nie swem nie.</strong></li></ul>"
                     "<p><strong>Only one nie</strong> when nothing follows the verb: <em>Ek eet.</em> - "
                     "<strong>Ek eet nie.</strong></p>"
                     "<p><strong>Negative words</strong> (these replace the positive word and still take a "
                     "<em>nie</em> at the end):</p><ul><li>iemand - <strong>niemand</strong>: <em>Niemand het "
                     "gebel nie.</em></li><li>iets - <strong>niks</strong>: <em>Ek het niks gekoop nie.</em>"
                     "</li><li>altyd - <strong>nooit</strong>: <em>Sy is nooit laat nie.</em></li>"
                     "<li>oral / êrens - <strong>nêrens</strong>: <em>Ek kan dit nêrens kry nie.</em></li>"
                     "<li>'n - <strong>geen</strong>: <em>Ek het geen geld nie.</em></li>"
                     "<li>al - <strong>nog nie</strong>: <em>Hy is al hier.</em> - <em>Hy is nog nie hier nie."
                     "</em></li><li>ja - <strong>nee</strong></li></ul>"
                     "<p><strong>Commands</strong>: <em>Moenie ... nie</em>: <em>Moenie in die gang hardloop "
                     "nie!</em></p>",
            'key_terms': [
                ('ontkenning', 'negation - making a sentence negative'),
                ('niemand', 'nobody (from iemand)'),
                ('niks', 'nothing (from iets)'),
                ('nooit', 'never (from altyd)'),
                ('nêrens', 'nowhere (from oral / êrens)'),
            ],
            'example': {
                'title': 'Uitgewerkte voorbeelde: ontken die sinne',
                'html': "<ol><li><em>Ja, ek het my huiswerk gedoen.</em> - <strong>Nee, ek het nie my huiswerk "
                        "gedoen nie.</strong></li><li><em>Iemand klop aan die deur.</em> - <strong>Niemand klop "
                        "aan die deur nie.</strong></li><li><em>Hy sê altyd iets snaaks.</em> - <strong>Hy sê "
                        "nooit iets snaaks nie.</strong> (Only one negative word is needed: <em>nooit</em> "
                        "replaces <em>altyd</em>; <em>iets</em> may stay.)</li><li><em>Ons het 'n kat.</em> - "
                        "<strong>Ons het geen kat nie.</strong></li><li><em>Ek lees.</em> - <strong>Ek lees "
                        "nie.</strong> (one nie)</li></ol>",
            },
            'video': {'id': 'ylQjP7StBKQ', 'title': 'Ontkennede vorm (The negative form) | Ontkenning | Afrikaans FAL',
                      'channel': 'Bad Teacher', 'minutes': 10},
            'worksheet': {
                'instructions': 'Skryf die sinne in die ontkennende vorm. (Write the sentences in the negative.)',
                'exercises': [
                    "1. Ek hou van spinasie.",
                    "2. Sy het die brief gestuur.",
                    "3. Iemand het my pen gevat.",
                    "4. Hy is altyd vriendelik.",
                    "5. Ek het iets in die kas gesien.",
                    "6. Ons het 'n motor.",
                    "7. Ja, die kinders slaap al.",
                    "8. Hardloop in die gang!",
                ],
            },
            'quiz': [
                ('mcq', "Negative of 'Ek speel sokker':",
                 ['Ek speel nie sokker.', 'Ek nie speel sokker nie.', 'Ek speel nie sokker nie.',
                  'Ek speel sokker nie.'], 2),
                ('mcq', "Negative of 'Iemand het geroep':",
                 ['Niemand het geroep nie.', 'Iemand het nie geroep.', 'Niks het geroep nie.',
                  'Nooit het iemand geroep.'], 0),
                ('tf', "'Ek slaap.' becomes 'Ek slaap nie.' with only one nie.", True),
                ('mcq', "The negative form of 'altyd' is...", ['niks', 'nêrens', 'nooit', 'geen'], 2),
                ('tf', "The negative of 'Hy is al hier' is 'Hy is nog nie hier nie.'", True),
            ],
            'homework': {
                'title': 'Ontkenning-oefening',
                'instructions': 'Practise the negative form in context.',
                'tasks': [
                    'Write eight positive sentences about your daily routine.',
                    'Rewrite all eight in the negative form.',
                    'Use niemand, niks, nooit and nêrens at least once each.',
                ],
                'marks': 16,
            },
        },
        {
            'title': 'Die formele brief: format and formal register',
            'minutes': 50,
            'objectives': [
                "Ek ken die formaat van 'n formele brief.",
                "Ek kan 'n formele brief van 120-150 woorde skryf (bv. 'n klagte of aansoek).",
                "Ek gebruik formele taal en die beleefde vorm 'u'.",
            ],
            'notes': "<p>A <strong>formele brief</strong> is written to a company, newspaper, principal or "
                     "official - for example to apply, complain or request information.</p>"
                     "<ol><li><strong>Adres van die skrywer</strong> - top right.</li><li><strong>Datum</strong>"
                     " - under your address.</li><li><strong>Adres van die ontvanger</strong> - on the left, "
                     "below the date.</li><li><strong>Aanhef</strong>: <em>Geagte Meneer / Mevrou</em> or "
                     "<em>Geagte mnr. Botha</em></li><li><strong>Onderwerp</strong> (subject line), underlined "
                     "or in capitals: <em>KLAGTE OOR SWAK DIENS</em> or <em>Insake: aansoek om 'n pos as "
                     "kassier</em></li><li><strong>Inleiding</strong> - state why you are writing.</li>"
                     "<li><strong>Liggaam</strong> - give facts and details in paragraphs.</li>"
                     "<li><strong>Slot</strong> - say what you would like to happen: <em>Ek sien uit na u "
                     "antwoord.</em></li><li><strong>Die uwe</strong> (Yours faithfully), signature, and your "
                     "full name.</li></ol>"
                     "<p><strong>Register</strong>: use formal language and <em>u</em>; no slang, no "
                     "abbreviations like <em>OK</em>, and no exclamation marks.</p>",
            'key_terms': [
                ('Geagte Meneer / Mevrou', 'Dear Sir / Madam'),
                ('Insake / onderwerp', 'subject line of a formal letter'),
                ('Die uwe', 'Yours faithfully'),
                ('formele register', 'formal, respectful language'),
            ],
            'example': {
                'title': "Voorbeeld: 'n klagtebrief (inleiding, liggaam en slot)",
                'html': "<p><em>Geagte Meneer</em></p><p><strong><em>KLAGTE OOR 'N FOUTIEWE SELFOON</em></strong>"
                        "</p><p><em>Ek skryf om te kla oor 'n selfoon wat ek op 5 Januarie 2026 by u winkel gekoop "
                        "het.</em></p><p><em>Die foon werk nie behoorlik nie. Die battery hou net twee uur en die "
                        "skerm het al twee keer gevries. Ek het die strokie en die waarborg nog.</em></p><p><em>"
                        "Ek versoek dat u die foon vervang of my geld terugbetaal. Ek sien uit na u antwoord."
                        "</em></p><p><em>Die uwe<br>(handtekening)<br>T. Nkosi</em></p><p>Notice: formal register, "
                        "<em>u</em>, a clear subject line and a clear request.</p>",
            },
            'video': {'id': 'uykiH1IfySc', 'title': 'Afrikaans Graad 12   Formele Brief',
                      'channel': 'Self Learning in the Bushveld', 'minutes': 10},
            'worksheet': {
                'instructions': 'Beantwoord die vrae oor die formele brief.',
                'exercises': [
                    '1. List the parts of a formal letter in the correct order.',
                    '2. Write a suitable aanhef for a letter to the principal, Mrs Dlamini.',
                    '3. Write a subject line for a letter applying for a part-time job at a bookshop.',
                    '4. Rewrite in formal register: "Hey, julle diens is regtig swak, man!"',
                    '5. Write an opening sentence for a letter of complaint about a late delivery.',
                    '6. Write the closing of a formal letter (slot, Die uwe, name).',
                ],
            },
            'quiz': [
                ('mcq', 'How do you close a formal letter in Afrikaans?',
                 ['Groete', 'Jou vriend', 'Die uwe', 'Baie liefde'], 2),
                ('mcq', 'Which aanhef is correct for a formal letter?',
                 ['Liewe Meneer,', 'Geagte Meneer', 'Haai Meneer!', 'Hallo daar,'], 1),
                ('tf', "In a formal letter you use 'u' to address the reader.", True),
                ('tf', 'Slang and exclamation marks are suitable in a formal letter.', False),
            ],
            'homework': {
                'title': 'Skryf \'n formele brief',
                'instructions': "Write a formal letter (120-150 words) to your municipality complaining about a broken streetlight in your street.",
                'tasks': [
                    'Use the full formal format, including both addresses, date and subject line.',
                    'Explain the problem and why it is dangerous.',
                    'Make a clear, polite request and close correctly with "Die uwe".',
                ],
                'marks': 20,
            },
        },
    ],
}

# ---------------------------------------------------------------------------
# ISIZULU ULIMI LOKUQALA OLWENGEZIWE (ZUL-FAL)
# ---------------------------------------------------------------------------

LESSONS[(10, 'ZUL-FAL')] = {
    'topic': 'Ukulalela nokukhuluma: ukubingelela nokuzethula; amabizo; ukubhala indima',
    'caps': "isiZulu FAL Gr 10 Ikota 1 Amaviki 1-2 (CAPS/ATP): Ukulalela nokukhuluma - ukubingelela, "
            "ukuzethula nengxoxo; Uhlelo lolimi - amabizo (iziqalo nezigaba zamabizo, ubunye nobuningi); "
            "Ukubhala nokwethula - indima emfushane ngawe.",
    'summary': "Learners greet respectfully and introduce themselves in isiZulu, learn how isiZulu nouns are "
               "built from a prefix and stem in noun classes, and write a short paragraph about themselves.",
    'days': [
        {
            'title': 'Ukubingelela nokuzethula: greetings and introductions',
            'minutes': 40,
            'objectives': [
                'Ngiyakwazi ukubingelela umuntu oyedwa nabantu abaningi (greet one person and a group).',
                'Ngiyakwazi ukuzethula: igama, iminyaka, indawo engihlala kuyo (introduce myself).',
                'Ngiyazi ukuthi ngisho "Hamba kahle" noma "Sala kahle" nini (know which goodbye to use).',
            ],
            'notes': "<p>Greeting is very important in isiZulu culture - always greet before you ask or say "
                     "anything else.</p>"
                     "<ul><li><strong>Sawubona</strong> - Hello (to one person). Reply: <em>Yebo, sawubona.</em>"
                     "</li><li><strong>Sanibonani</strong> - Hello (to more than one person, or to an elder to "
                     "show respect). Reply: <em>Yebo, sanibonani.</em></li>"
                     "<li><strong>Unjani?</strong> - How are you? (one person) - <em>Ngiyaphila, wena "
                     "unjani?</em> (I am well, and you?)</li><li><strong>Ninjani?</strong> - How are you? "
                     "(many) - <em>Siyaphila, nina ninjani?</em></li>"
                     "<li><strong>Ngubani igama lakho?</strong> - What is your name? - <em>Igama lami "
                     "nguThandi.</em></li><li><strong>Uhlala kuphi?</strong> - Where do you live? - "
                     "<em>Ngihlala eThekwini.</em> (I live in Durban.)</li>"
                     "<li><strong>Ufunda ibanga lesingaki?</strong> - Which grade are you in? - <em>Ngifunda "
                     "ibanga leshumi.</em> (Grade 10.)</li><li><strong>Ngiyajabula ukukwazi.</strong> - "
                     "Pleased to meet you.</li><li><strong>Ngiyabonga.</strong> - Thank you.</li></ul>"
                     "<p><strong>Saying goodbye:</strong> the person <em>leaving</em> says <strong>Sala kahle"
                     "</strong> (stay well); the person <em>staying</em> says <strong>Hamba kahle</strong> "
                     "(go well).</p><p>Show respect to adults: <em>Sawubona baba</em> (to a man), "
                     "<em>Sawubona mama</em> (to a woman), or use the plural <em>Sanibonani</em>.</p>",
            'key_terms': [
                ('Sawubona / Sanibonani', 'Hello (to one person / to many or to an elder)'),
                ('Unjani? / Ninjani?', 'How are you? (one / many)'),
                ('Ngiyaphila', 'I am well'),
                ('Hamba kahle / Sala kahle', 'Go well (to the one leaving) / Stay well (to the one staying)'),
                ('Ngiyabonga', 'Thank you'),
            ],
            'example': {
                'title': 'Ingxoxo: umngane omusha (role-play in groups of three)',
                'html': "<p><strong>Thandi:</strong> Sawubona, Lwazi!<br><strong>Lwazi:</strong> Yebo, "
                        "sawubona Thandi. Unjani?<br><strong>Thandi:</strong> Ngiyaphila, ngiyabonga. Wena "
                        "unjani?<br><strong>Lwazi:</strong> Nami ngiyaphila. Lo ngubani?<br><strong>Thandi:"
                        "</strong> Lo ngumngane wami omusha. Igama lakhe nguPieter.<br><strong>Pieter:</strong> "
                        "Sawubona Lwazi. Ngiyajabula ukukwazi.<br><strong>Lwazi:</strong> Nami ngiyajabula. "
                        "Uhlala kuphi, Pieter?<br><strong>Pieter:</strong> Ngihlala ePitoli.<br><strong>Lwazi:"
                        "</strong> Kuhle! Sala kahle, ngiya ekilasini.<br><strong>Thandi noPieter:</strong> "
                        "Hamba kahle!</p><p>English: Lwazi is leaving, so he says <em>Sala kahle</em> and the "
                        "others answer <em>Hamba kahle</em>.</p>",
            },
            'video': {'id': 'A6o5Mrrd4Ww',
                      'title': 'Learn isiZulu Greetings | How to Greet & Respond in Zulu for Beginners',
                      'channel': 'Zulu Lessons with Thando', 'minutes': 8},
            'worksheet': {
                'instructions': 'Phendula imibuzo ngesiZulu. (Answer the questions in isiZulu.)',
                'exercises': [
                    '1. Ngubani igama lakho?',
                    '2. Uhlala kuphi?',
                    '3. Ufunda ibanga lesingaki?',
                    '4. How do you greet a class of learners? Write the greeting and the reply.',
                    '5. Your friend is leaving your house. What do you say to her?',
                    '6. Translate: "I am well, thank you. And you?"',
                    '7. Write a dialogue of 6 lines in which you meet a new learner.',
                ],
            },
            'quiz': [
                ('mcq', 'How do you greet a group of people?',
                 ['Sawubona', 'Sanibonani', 'Hamba kahle', 'Ngiyabonga'], 1),
                ('mcq', 'Someone asks "Unjani?" The best answer is...',
                 ['Ngiyaphila, wena unjani?', 'Igama lami nguSipho.', 'Ngihlala eGoli.', 'Sala kahle.'], 0),
                ('tf', 'The person who is leaving says "Sala kahle" to the person who stays.', True),
                ('mcq', 'What does "Ngiyabonga" mean?',
                 ['Goodbye', 'Hello', 'Thank you', 'I am well'], 2),
            ],
            'homework': {
                'title': 'Zethule (introduce yourself)',
                'instructions': 'Prepare a short oral introduction of yourself in isiZulu to present in class.',
                'tasks': [
                    'Write 5-6 sentences: greeting, name, where you live, grade and one thing you like.',
                    'Practise saying it aloud to a family member or record yourself.',
                    'Teach someone at home three isiZulu greetings and their replies.',
                ],
                'marks': 10,
            },
        },
        {
            'title': 'Amabizo: nouns, prefixes and noun classes',
            'minutes': 45,
            'objectives': [
                'Ngiyakwazi ukuhlukanisa isiqalo nomsuka webizo (prefix and stem).',
                'Ngiyakwazi ukushintsha ibizo kusuka ebunyeni kuya ebuningini (singular to plural).',
                'I can name the noun-class pairs 1/2, 3/4, 5/6, 7/8 and 9/10 with examples.',
            ],
            'notes': "<p>Every isiZulu noun (<strong>ibizo</strong>, plural <strong>amabizo</strong>) has two "
                     "parts: a <strong>prefix</strong> (<em>isiqalo</em>) and a <strong>stem</strong> "
                     "(<em>umsuka</em>). Example: <em>um-fana</em> (boy) = prefix <em>um-</em> + stem "
                     "<em>-fana</em>. The prefix shows the <strong>noun class</strong> (<em>isigaba</em>) and "
                     "whether the noun is singular (<em>ubunye</em>) or plural (<em>ubuningi</em>).</p>"
                     "<ul><li><strong>Class 1/2 (um-/umu- : aba-)</strong> - people: <em>umfana - abafana</em>, "
                     "<em>umuntu - abantu</em>, <em>umfundi - abafundi</em></li>"
                     "<li><strong>Class 1a/2a (u- : o-)</strong> - kinship and names: <em>umama - omama</em>, "
                     "<em>ubaba - obaba</em></li><li><strong>Class 3/4 (um-/umu- : imi-)</strong> - "
                     "<em>umuthi - imithi</em> (tree), <em>umfula - imifula</em> (river)</li>"
                     "<li><strong>Class 5/6 (i-/ili- : ama-)</strong> - <em>iqanda - amaqanda</em> (egg), "
                     "<em>ibhola - amabhola</em></li><li><strong>Class 7/8 (isi- : izi-)</strong> - "
                     "<em>isikole - izikole</em> (school), <em>isitsha - izitsha</em> (dish)</li>"
                     "<li><strong>Class 9/10 (in-/im- : izin-/izim-)</strong> - <em>inja - izinja</em> (dog), "
                     "<em>incwadi - izincwadi</em> (book/letter), <em>imbuzi - izimbuzi</em> (goat)</li></ul>"
                     "<p>Other classes: <strong>ubu-</strong> (class 14, abstract nouns: <em>ubuhle</em> - "
                     "beauty) and <strong>uku-</strong> (class 15, verbal nouns: <em>ukudla</em> - food / "
                     "eating).</p>",
            'key_terms': [
                ('ibizo / amabizo', 'noun / nouns'),
                ('isiqalo', 'prefix'),
                ('umsuka', 'stem'),
                ('ubunye / ubuningi', 'singular / plural'),
                ('isigaba', 'noun class'),
            ],
            'example': {
                'title': 'Isibonelo: ubunye nobuningi (worked example: singular to plural)',
                'html': "<ol><li><em>umfundi</em> (learner) - prefix <em>um-</em>, stem <em>-fundi</em>, class 1 "
                        "- plural <strong>abafundi</strong> (class 2)</li><li><em>isihlalo</em> (chair) - prefix "
                        "<em>isi-</em> - plural <strong>izihlalo</strong></li><li><em>itafula</em> (table) - "
                        "prefix <em>i-</em> - plural <strong>amatafula</strong></li><li><em>imoto</em> (car) - "
                        "class 9 - plural <strong>izimoto</strong></li><li><em>umuthi</em> (tree / medicine) - "
                        "class 3 - plural <strong>imithi</strong></li></ol><p>Tip: first find the prefix, then "
                        "match it to its plural partner.</p>",
            },
            'video': {'id': 'RT3Xo5o2WjE', 'title': 'IsiZulu Noun Classes explained!',
                      'channel': 'Zamani Zulu - Learn isiZulu', 'minutes': 10},
            'worksheet': {
                'instructions': 'Bhala ubuningi bala mabizo. (Write the plural of these nouns.) Underline the prefix.',
                'exercises': [
                    '1. umfana',
                    '2. isikole',
                    '3. iqanda',
                    '4. inja',
                    '5. umfula',
                    '6. ubaba',
                    '7. incwadi',
                    '8. Write the singular of: abantu, izitsha, amabhola.',
                ],
            },
            'quiz': [
                ('mcq', 'What is the plural of "isikole" (school)?',
                 ['amakole', 'izikole', 'abakole', 'imikole'], 1),
                ('mcq', 'In "umfana", the prefix is...', ['-fana', 'um-', 'fa-', 'na-'], 1),
                ('tf', 'The plural of "inja" (dog) is "izinja".', True),
                ('mcq', 'Which noun is plural?', ['umuntu', 'iqanda', 'imithi', 'isitsha'], 2),
                ('tf', 'The plural of "umama" is "abamama".', False),
            ],
            'homework': {
                'title': 'Amabizo asekhaya (nouns at home)',
                'instructions': 'Find objects and people at home and name them in isiZulu (use a dictionary if needed).',
                'tasks': [
                    'Write 10 isiZulu nouns for things or people at home.',
                    'Write the plural of each and underline the prefixes.',
                    'Group your nouns by noun class.',
                ],
                'marks': 15,
            },
        },
        {
            'title': 'Ukubhala indima ngami: writing a paragraph about myself',
            'minutes': 45,
            'objectives': [
                'Ngiyakwazi ukubhala indima emfushane ngami (write a short paragraph about myself).',
                'I can use the subject concord "ngi-" (I) correctly with verbs.',
                'I can use nouns from Day 2 correctly in sentences.',
            ],
            'notes': "<p>Today you combine the greetings and nouns you learnt to write an <strong>indima</strong>"
                     " (paragraph) about yourself.</p>"
                     "<p><strong>The subject concord ngi- (I)</strong>: put <em>ngi-</em> in front of the verb "
                     "stem: <em>-hlala</em> (live) - <strong>ngihlala</strong> (I live), <em>-funda</em> (learn) "
                     "- <strong>ngifunda</strong>, <em>-thanda</em> (like/love) - <strong>ngithanda</strong>.</p>"
                     "<p><strong>Useful sentences</strong></p><ul><li><em>Igama lami nguLerato.</em> - My name is "
                     "Lerato.</li><li><em>Ngineminyaka eyishumi nanhlanu.</em> - I am fifteen years old.</li>"
                     "<li><em>Ngihlala eSoweto nomama nabafowethu ababili.</em> - I live in Soweto with my "
                     "mother and two brothers.</li><li><em>Ngifunda ibanga leshumi.</em> - I am in Grade 10."
                     "</li><li><em>Isifundo engisithanda kakhulu yiZibalo.</em> - My favourite subject is "
                     "Mathematics.</li><li><em>Ngithanda ukudlala ibhola nokulalela umculo.</em> - I like "
                     "playing soccer and listening to music.</li><li><em>Ngifuna ukuba ngudokotela.</em> - I "
                     "want to be a doctor.</li></ul>"
                     "<p>Structure: start with a sentence that introduces you, add details, and end with your "
                     "dream for the future. Check the capital letter after the prefix in names: "
                     "<em>nguLerato, eSoweto, eThekwini</em>.</p>",
            'key_terms': [
                ('indima', 'paragraph'),
                ('ngi-', 'subject concord for "I"'),
                ('Ngithanda...', 'I like / love...'),
                ('Ngifuna ukuba ngu...', 'I want to be a...'),
            ],
            'example': {
                'title': 'Isibonelo sendima (example paragraph)',
                'html': "<p><em>Sanibonani! Igama lami nguLerato Mokoena. Ngineminyaka eyishumi nanhlanu. "
                        "Ngihlala eSoweto nomama nabafowethu ababili. Ngifunda ibanga leshumi. Isifundo "
                        "engisithanda kakhulu yiZibalo. Ngithanda ukudlala ibhola nokulalela umculo. Ngifuna "
                        "ukuba ngudokotela. Ngiyabonga.</em></p><p>English: Hello everyone! My name is Lerato "
                        "Mokoena. I am fifteen years old. I live in Soweto with my mother and my two brothers. "
                        "I am in Grade 10. My favourite subject is Mathematics. I like playing soccer and "
                        "listening to music. I want to be a doctor. Thank you.</p>",
            },
            'video': {'id': 'ZJyCnTVKGmc',
                      'title': 'Learn isiZulu: How to Introduce Yourself Fully (Name, Siblings, Work, City, Study)',
                      'channel': 'Zulu Lessons with Thando', 'minutes': 10},
            'worksheet': {
                'instructions': 'Qedela imisho, bese ubhala indima. (Complete the sentences, then write a paragraph.)',
                'exercises': [
                    '1. Igama lami ngu________.',
                    '2. Ngihlala e________.',
                    '3. Ngifunda ibanga ________.',
                    '4. Add ngi- to the verb: ___thanda umculo. (I like music.)',
                    '5. Translate: "I want to be a teacher." (teacher = uthisha)',
                    '6. Write a paragraph of 6-8 sentences about yourself in isiZulu.',
                ],
            },
            'quiz': [
                ('mcq', 'How do you say "I live in Durban"?',
                 ['Uhlala eThekwini.', 'Ngihlala eThekwini.', 'Bahlala eThekwini.', 'Sihlala eThekwini.'], 1),
                ('mcq', '"Ngifunda ibanga leshumi" means...',
                 ['I am in Grade 10.', 'I like reading.', 'I am ten years old.', 'I live at school.'], 0),
                ('tf', 'The subject concord "ngi-" means "I".', True),
                ('mcq', 'Which sentence means "I like music"?',
                 ['Ngithanda umculo.', 'Uthanda umculo.', 'Ngifuna umculo.', 'Ngihlala umculo.'], 0),
            ],
            'homework': {
                'title': 'Indima: umndeni wami (my family)',
                'instructions': 'Write a short paragraph in isiZulu about your family.',
                'tasks': [
                    'Write 6-8 sentences with the names of family members and where you live.',
                    'Use at least three nouns from Day 2 and three verbs with ngi-.',
                    'Give your paragraph a title and read it aloud at home.',
                ],
                'marks': 15,
            },
        },
    ],
}

LESSONS[(11, 'ZUL-FAL')] = {
    'topic': 'Ukufunda nokubuka: indaba emfushane; izenzo nezinkathi',
    'caps': "isiZulu FAL Gr 11 Ikota 1 Amaviki 1-2 (CAPS/ATP): Ukufunda nokubuka - indaba emfushane "
            "(isakhiwo sendaba, abalingiswa, indawo, ingqikithi) nokufunda ngokuqondisisa; Uhlelo lolimi - "
            "izenzo (isivumelwano somenzi, inkathi yamanje, edlule nezayo, ukuphika).",
    'summary': "Learners read and analyse a short story in isiZulu, discuss its structure, characters and "
               "theme, and practise verb tenses and the negative using sentences from the story.",
    'days': [
        {
            'title': 'Isakhiwo sendaba emfushane: the structure of a short story',
            'minutes': 45,
            'objectives': [
                'Ngiyakwazi ukuchaza isakhiwo sendaba emfushane (explain the structure of a short story).',
                'Ngiyakwazi ukuphendula imibuzo ngendaba engiyifundile (answer questions on a story).',
                'I can identify the conflict (ingxabano) and climax (uvuthondaba).',
            ],
            'notes': "<p>An <strong>indaba emfushane</strong> (short story) has a small number of characters "
                     "and focuses on one main event. Its <strong>isakhiwo</strong> (structure / plot) usually "
                     "has these parts:</p>"
                     "<ol><li><strong>Isingeniso</strong> (introduction) - we meet the characters and the "
                     "setting.</li><li><strong>Ukukhula kwesigameko</strong> (rising action) - a problem or "
                     "<em>ingxabano</em> (conflict) develops.</li><li><strong>Uvuthondaba</strong> (climax) - "
                     "the turning point with the most tension.</li><li><strong>Isixazululo</strong> "
                     "(resolution) - the conflict is solved.</li><li><strong>Isiphetho</strong> (ending) - how "
                     "the story ends.</li></ol>"
                     "<p><strong>Ingxabano</strong> can be <em>yangaphakathi</em> (internal - inside a "
                     "character's mind) or <em>yangaphandle</em> (external - with another person, society or "
                     "nature).</p><p>When reading, first read for general understanding, then read again and "
                     "underline new words. Use the context to guess their meaning.</p>",
            'key_terms': [
                ('indaba emfushane', 'short story'),
                ('isakhiwo', 'structure / plot'),
                ('ingxabano', 'conflict'),
                ('uvuthondaba', 'climax'),
                ('isiphetho', 'ending'),
            ],
            'example': {
                'title': 'Funda ndawonye: "Ibhayisikili" (read together)',
                'html': "<p><em>USipho wayefunda ibanga leshumi nanye. Wayefuna kakhulu ukuthenga ibhayisikili "
                        "elisha. Njalo ngoMgqibelo wayesebenza esitolo. Ngelinye ilanga wabona umfowabo "
                        "omncane, uThemba, ekhala. Izicathulo zikaThemba zazidabukile. USipho wacabanga "
                        "isikhathi eside. Ngakusasa wamthengela uThemba izicathulo ezintsha. Ibhayisikili "
                        "lalizolinda, kodwa ukumamatheka kukaThemba kwakubaluleke kakhulu kuye.</em></p>"
                        "<ul><li><strong>Isingeniso:</strong> Sipho saves money for a bicycle.</li>"
                        "<li><strong>Ingxabano:</strong> yangaphakathi - bicycle or his brother's shoes?</li>"
                        "<li><strong>Uvuthondaba:</strong> Sipho thinks for a long time (wacabanga isikhathi "
                        "eside).</li><li><strong>Isixazululo / isiphetho:</strong> he buys Themba new shoes and "
                        "is happy with his choice.</li></ul>",
            },
            'video': {'id': 'sNkXnzc3b4A', 'title': 'Isakhiwo Sendaba Emfushane - EXPLAINED VERY WELL',
                      'channel': 'TheStream', 'minutes': 10},
            'worksheet': {
                'instructions': 'Funda indaba ethi "Ibhayisikili" bese uphendula imibuzo. (Answer in isiZulu or English as instructed.)',
                'exercises': [
                    '1. USipho wayefunda ibanga lesingaki?',
                    '2. USipho wayefuna ukuthenga ini?',
                    '3. USipho wayesebenza nini?',
                    '4. Kungani uThemba ayekhala? (Why was Themba crying?)',
                    '5. Is the conflict yangaphakathi or yangaphandle? Explain in English.',
                    '6. Which sentence shows the uvuthondaba (climax)?',
                    '7. What does "izicathulo" mean? Use the context.',
                ],
            },
            'quiz': [
                ('mcq', '"Uvuthondaba" in a short story is the...',
                 ['introduction', 'climax', 'title', 'setting'], 1),
                ('mcq', 'In the story, what did Sipho buy in the end?',
                 ['a bicycle', 'a book', 'shoes for Themba', 'food'], 2),
                ('tf', 'Ingxabano yangaphakathi is a conflict inside a character\'s mind.', True),
                ('tf', '"Isingeniso" is the ending of a story.', False),
            ],
            'homework': {
                'title': 'Isakhiwo sendaba',
                'instructions': 'Read an isiZulu short story from your textbook (or retell a story you know).',
                'tasks': [
                    'Write the title and the names of the main characters.',
                    'Draw the plot structure and write one sentence for each part (isingeniso to isiphetho).',
                    'Is the conflict yangaphakathi or yangaphandle? Explain.',
                ],
                'marks': 10,
            },
        },
        {
            'title': 'Abalingiswa, indawo nengqikithi: characters, setting and theme',
            'minutes': 45,
            'objectives': [
                'Ngiyakwazi ukuchaza umlingiswa omkhulu nabalingiswa abasizayo (describe characters).',
                'I can describe the setting (indawo nesikhathi) of a story.',
                'I can state the theme (ingqikithi) of a story in a sentence.',
            ],
            'notes': "<p><strong>Abalingiswa</strong> (characters) bring a story to life.</p>"
                     "<ul><li><strong>Umlingiswa omkhulu</strong> - the main character (protagonist), e.g. "
                     "Sipho.</li><li><strong>Umphikisi</strong> - the character or force against the main "
                     "character (antagonist).</li><li><strong>Abalingiswa abasizayo</strong> - supporting "
                     "characters, e.g. Themba.</li></ul>"
                     "<p>We learn about characters from what they <em>do</em>, what they <em>say</em> and what "
                     "others say about them. Describe a character with an adjective and evidence: "
                     "<em>USipho unothando ngoba wamthengela umfowabo izicathulo.</em> (Sipho is loving because "
                     "he bought his brother shoes.)</p>"
                     "<p><strong>Indawo</strong> (setting) is where and <strong>isikhathi</strong> when the "
                     "story happens: <em>esitolo, ekhaya, ngoMgqibelo</em>.</p>"
                     "<p><strong>Ingqikithi</strong> (theme) is the main message: <em>Uthando lomndeni "
                     "lubaluleke ukwedlula izinto.</em> (Family love is more important than possessions.)</p>"
                     "<p><strong>Umlandisi</strong> (narrator) may tell the story in the first person "
                     "(<em>mina</em>) or third person (<em>yena</em>).</p>",
            'key_terms': [
                ('abalingiswa', 'characters'),
                ('umlingiswa omkhulu', 'main character'),
                ('indawo', 'setting (place)'),
                ('ingqikithi', 'theme'),
                ('umlandisi', 'narrator'),
            ],
            'example': {
                'title': 'Umsebenzi wekilasi: character chart',
                'html': "<p>In groups, complete a chart for the story <em>Ibhayisikili</em>:</p><ul><li><strong>"
                        "USipho</strong> - umlingiswa omkhulu; <em>uyakhuthala</em> (hardworking - he works "
                        "every Saturday); <em>unothando</em> (loving - he buys his brother shoes).</li>"
                        "<li><strong>UThemba</strong> - umlingiswa osizayo; his torn shoes cause the conflict."
                        "</li><li><strong>Indawo:</strong> esitolo nasekhaya; <strong>isikhathi:</strong> "
                        "ngoMgqibelo nangakusasa.</li><li><strong>Umlandisi:</strong> third person (USipho "
                        "wayefuna... - he wanted...).</li><li><strong>Ingqikithi:</strong> Uthando lomndeni "
                        "lubaluleke ukwedlula izinto.</li></ul>",
            },
            'video': {'id': 'QGnSZnIAjSs', 'title': 'Izinhlobo zabalingiswa |  indaba emfushane | inoveli',
                      'channel': 'TheStream', 'minutes': 10},
            'worksheet': {
                'instructions': 'Phendula imibuzo ngendaba ethi "Ibhayisikili".',
                'exercises': [
                    '1. Ngubani umlingiswa omkhulu?',
                    '2. Name the supporting character and explain his role in the story.',
                    '3. Give one isiZulu adjective that describes Sipho and give evidence from the story.',
                    '4. Where (indawo) does the story take place? Name two places.',
                    '5. Is the umlandisi first person or third person? How do you know?',
                    '6. Write the ingqikithi of the story in one sentence (isiZulu or English).',
                ],
            },
            'quiz': [
                ('mcq', '"Ingqikithi" of a story is its...', ['setting', 'theme', 'title', 'narrator'], 1),
                ('mcq', 'Who is the main character (umlingiswa omkhulu) in "Ibhayisikili"?',
                 ['UThemba', 'USipho', 'Umama', 'Umnikazi wesitolo'], 1),
                ('tf', '"Indawo" refers to where a story takes place.', True),
                ('tf', 'A third-person narrator tells the story using "mina" (I).', False),
            ],
            'homework': {
                'title': 'Chaza umlingiswa (describe a character)',
                'instructions': 'Choose a character from an isiZulu story, TV drama or film you know.',
                'tasks': [
                    'Write the name of the character and whether he/she is the main or a supporting character.',
                    'Describe the character with three qualities and evidence for each.',
                    'Write the theme of the story in one sentence.',
                ],
                'marks': 12,
            },
        },
        {
            'title': 'Izenzo nezinkathi: verbs, tenses and the negative',
            'minutes': 45,
            'objectives': [
                'Ngiyakwazi ukusebenzisa izivumelwano zomenzi (subject concords) nezenzo.',
                'I can change a verb into the present, past and future tense.',
                'I can make a present-tense verb negative (ukuphika).',
            ],
            'notes': "<p>An isiZulu verb (<strong>isenzo</strong>) is built from a <strong>subject concord"
                     "</strong> (<em>isivumelwano somenzi</em>) + a verb stem. Subject concords: <em>ngi-</em> "
                     "(I), <em>u-</em> (you / he / she), <em>si-</em> (we), <em>ni-</em> (you pl.), <em>ba-</em> "
                     "(they - people).</p>"
                     "<p><strong>Inkathi yamanje</strong> (present): <em>Ngiyafunda.</em> (I am reading.) "
                     "When an object follows, drop <em>-ya-</em>: <em>Ngifunda incwadi.</em></p>"
                     "<p><strong>Inkathi edlule</strong> (past): <em>Ngifundile.</em> (I have read.) With an "
                     "object: <em>Ngifunde incwadi.</em> The remote past: <em>Ngafunda</em> (I read, long "
                     "ago).</p><p><strong>Inkathi ezayo</strong> (future): <em>Ngizofunda.</em> (I will read.)"
                     " <em>Ngizofunda incwadi.</em></p>"
                     "<p><strong>Ukuphika</strong> (negative, present): put <em>a-</em> before the concord and "
                     "change the final <em>-a</em> to <em>-i</em>: <em>Ngiyadlala - Angidlali</em> (I don't "
                     "play), <em>Siyadlala - Asidlali</em>, <em>Bayadlala - Abadlali</em>. Note: for he/she "
                     "it is <em>Akadlali</em> and for you <em>Awudlali</em>. Past negative: <em>Ngidlalile - "
                     "Angidlalanga</em> (I did not play).</p>",
            'key_terms': [
                ('isenzo / izenzo', 'verb / verbs'),
                ('isivumelwano somenzi', 'subject concord'),
                ('inkathi yamanje / edlule / ezayo', 'present / past / future tense'),
                ('ukuphika', 'the negative'),
            ],
            'example': {
                'title': 'Isibonelo: sentences from the story in three tenses',
                'html': "<ul><li>Present: <strong>USipho usebenza esitolo.</strong> (Sipho works at the shop.)"
                        "</li><li>Past: <strong>USipho usebenze esitolo.</strong> (Sipho worked at the shop.)</li>"
                        "<li>Future: <strong>USipho uzosebenza esitolo.</strong> (Sipho will work at the shop.)"
                        "</li><li>Negative (present): <strong>USipho akasebenzi esitolo.</strong> (Sipho does not "
                        "work at the shop.)</li><li>With I: <strong>Ngiyasebenza - Ngisebenzile - Ngizosebenza - "
                        "Angisebenzi.</strong></li></ul>",
            },
            'video': {'id': 'H7hPpshDqgk', 'title': 'Verbs (izenzo) in IsiZulu',
                      'channel': 'IsiZulu Tutoring with Teacher Ximba', 'minutes': 10},
            'worksheet': {
                'instructions': 'Bhala imisho ngenkathi ekubakaki. (Rewrite in the tense in brackets.)',
                'exercises': [
                    '1. Ngiyadlala. (inkathi edlule)',
                    '2. Sifunda incwadi. (inkathi ezayo)',
                    '3. Bayacula. (inkathi edlule)',
                    '4. Ngizopheka. (inkathi yamanje)',
                    '5. Ngiyabhala. (ukuphika - negative)',
                    '6. Bayahamba. (ukuphika - negative)',
                    '7. Write three sentences about your weekend using the past tense with ngi-.',
                ],
            },
            'quiz': [
                ('mcq', 'What is the future tense of "Ngiyafunda"?',
                 ['Ngifundile', 'Ngizofunda', 'Angifundi', 'Ngafunda'], 1),
                ('mcq', 'The negative of "Ngiyadlala" (I play) is...',
                 ['Angidlali', 'Ngidlalile', 'Ngizodlala', 'Asidlali'], 0),
                ('tf', '"Ba-" is the subject concord for "they" (people).', True),
                ('mcq', '"Ngifundile" is in the...', ['present tense', 'future tense', 'past tense', 'negative'], 2),
            ],
            'homework': {
                'title': 'Usuku lwami (my day)',
                'instructions': 'Write about your day using different tenses in isiZulu.',
                'tasks': [
                    'Write three sentences about what you did yesterday (past tense).',
                    'Write three sentences about what you will do tomorrow (future tense).',
                    'Write two negative sentences about things you do not do.',
                ],
                'marks': 16,
            },
        },
    ],
}

LESSONS[(12, 'ZUL-FAL')] = {
    'topic': 'Izinkondlo: izifengqo nokuhlaziya inkondlo; incwadi esemthethweni',
    'caps': "isiZulu FAL Gr 12 Ikota 1 Amaviki 1-2 (CAPS/ATP): Ukufunda nokubuka - izinkondlo "
            "(isakhiwo sangaphandle nesangaphakathi, izifengqo, umoya, ingqikithi; imibuzo esekelwe "
            "kumongo); Ukubhala nokwethula - umbhalo omude wokudlulisa umyalezo: incwadi esemthethweni.",
    'summary': "Matric learners identify and explain figures of speech in isiZulu poetry, analyse a poem's "
               "external and internal structure, and write a formal letter in the correct format.",
    'days': [
        {
            'title': 'Izifengqo: figures of speech in isiZulu poetry',
            'minutes': 45,
            'objectives': [
                'Ngiyakwazi ukubona isifaniso, isingathekiso, isenzasamuntu nehaba.',
                'I can explain the meaning and effect of a figure of speech.',
                'I can recognise repetition (ukuphindaphinda) in a poem.',
            ],
            'notes': "<p>Poets (<strong>izimbongi</strong>) use <strong>izifengqo</strong> (figures of speech) "
                     "to create pictures and feelings.</p>"
                     "<ul><li><strong>Isifaniso</strong> (simile) - compares using <em>njenga-/njengo-</em> "
                     "(like) or <em>-fana na-</em>: <em>Unamandla njengendlovu.</em> (He is as strong as an "
                     "elephant.)</li><li><strong>Isingathekiso</strong> (metaphor) - says one thing <em>is</em> "
                     "another: <em>UThemba yibhubesi.</em> (Themba is a lion - he is brave.)</li>"
                     "<li><strong>Isenzasamuntu</strong> (personification) - gives human actions to things: "
                     "<em>Ilanga liyamamatheka.</em> (The sun smiles.) <em>Umoya uyahlabelela.</em> (The wind "
                     "sings.)</li><li><strong>Ihaba</strong> (hyperbole) - exaggeration: <em>Ngilambe "
                     "ngingadla inkomo yonke.</em> (I am so hungry I could eat a whole cow.)</li>"
                     "<li><strong>Ukuphindaphinda</strong> (repetition) - repeating words or lines for "
                     "emphasis and rhythm.</li></ul>"
                     "<p>In the exam: name the figure of speech, quote it, and explain what it means and why "
                     "the poet used it.</p>",
            'key_terms': [
                ('imbongi', 'poet'),
                ('izifengqo', 'figures of speech'),
                ('isifaniso', 'simile'),
                ('isingathekiso', 'metaphor'),
                ('isenzasamuntu', 'personification'),
            ],
            'example': {
                'title': 'Hlaziya ndawonye: "Ilanga" (a short poem for class)',
                'html': "<p><em>Ilanga liyaphuma emagqumeni,<br>liyamamatheka phezu kwamasimu.<br>Ngiyalibona, "
                        "ngiyalibona,<br>linjengomlilo ovuthayo esibhakabhakeni.</em></p><p>English: The sun "
                        "rises from the hills, / it smiles over the fields. / I see it, I see it, / it is like a "
                        "burning fire in the sky.</p><ul><li><strong>Isenzasamuntu:</strong> "
                        "'liyamamatheka' - the sun smiles like a person; the morning feels warm and happy.</li>"
                        "<li><strong>Ukuphindaphinda:</strong> 'Ngiyalibona, ngiyalibona' - shows the speaker's "
                        "excitement.</li><li><strong>Isifaniso:</strong> 'linjengomlilo ovuthayo' - the sun is "
                        "compared to a burning fire, showing its heat and brightness.</li></ul>",
            },
            'video': {'id': 'SEQRMgu9PA8',
                      'title': 'Izifengqo (Figures of Speech): Isifaniso (Simile) & Isenzasamuntu (Personification)✍️🏾',
                      'channel': 'Usiba Luka Zulu', 'minutes': 8},
            'worksheet': {
                'instructions': 'Bhala isifengqo esisetshenzisiwe bese uchaza umqondo waso. (Name the figure of speech and explain it.)',
                'exercises': [
                    '1. Ugijima njengenyamazane.',
                    '2. UMandla yindlovu.',
                    '3. Imithi iyadansa emoyeni.',
                    '4. Ngikhathele ngingalala unyaka wonke.',
                    '5. Hamba, hamba, hamba mntanami.',
                    '6. Write your own isifaniso using "njenga-".',
                ],
            },
            'quiz': [
                ('mcq', '"Unamandla njengendlovu" is an example of...',
                 ['isingathekiso', 'isifaniso', 'ihaba', 'isenzasamuntu'], 1),
                ('mcq', '"Ilanga liyamamatheka" (the sun smiles) is...',
                 ['isenzasamuntu', 'isifaniso', 'ukuphindaphinda', 'ihaba'], 0),
                ('tf', '"Isingathekiso" is a metaphor.', True),
                ('mcq', 'What is an "imbongi"?', ['a short story', 'a poet', 'a letter', 'a noun'], 1),
            ],
            'homework': {
                'title': 'Izifengqo empilweni (figures of speech around you)',
                'instructions': 'Find figures of speech in isiZulu songs, praise poems or your poetry anthology.',
                'tasks': [
                    'Write down four examples, each a different figure of speech.',
                    'Name each figure of speech and explain its meaning in English or isiZulu.',
                    'Write two lines of your own poem using isenzasamuntu.',
                ],
                'marks': 12,
            },
        },
        {
            'title': 'Ukuhlaziya inkondlo: analysing a poem step by step',
            'minutes': 50,
            'objectives': [
                'Ngiyakwazi ukuhlaziya isakhiwo sangaphandle senkondlo (external structure).',
                'I can explain the literal meaning (umqondo osobala) and deeper meaning (umqondo ocashile).',
                'I can describe the mood (umoya) and theme (ingqikithi) of a poem.',
            ],
            'notes': "<p>Use these steps to analyse any isiZulu poem:</p>"
                     "<ol><li><strong>Isihloko</strong> (title) - what does it tell you?</li>"
                     "<li><strong>Imbongi</strong> (poet) - who wrote it?</li>"
                     "<li><strong>Isakhiwo sangaphandle</strong> (external structure) - how many "
                     "<em>izigaba</em> (stanzas) and <em>imigqa</em> (lines) are there? Is there "
                     "<em>isigqi</em> (rhythm) or repetition?</li>"
                     "<li><strong>Umqondo osobala</strong> - the surface / literal meaning: what is the poem "
                     "about?</li><li><strong>Umqondo ocashile</strong> - the hidden / deeper meaning.</li>"
                     "<li><strong>Isakhiwo sangaphakathi</strong> (internal structure) - izifengqo, word "
                     "choice and images.</li><li><strong>Umoya</strong> (mood) - happy, sad, angry, peaceful?"
                     "</li><li><strong>Ingqikithi</strong> (theme / main message).</li></ol>"
                     "<p>In contextual questions, read the mark allocation, quote from the poem to support "
                     "your answer, and write in full sentences.</p>",
            'key_terms': [
                ('isigaba / izigaba', 'stanza / stanzas'),
                ('umugqa / imigqa', 'line / lines of a poem'),
                ('umqondo osobala', 'literal (surface) meaning'),
                ('umqondo ocashile', 'hidden (deeper) meaning'),
                ('umoya', 'mood'),
            ],
            'example': {
                'title': 'Isibonelo: analysing "Ilanga"',
                'html': "<ul><li><strong>Isakhiwo sangaphandle:</strong> one stanza (isigaba esisodwa) of four "
                        "lines (imigqa emine); line 3 uses repetition.</li><li><strong>Umqondo osobala:</strong> "
                        "the sun rises over the hills and fields.</li><li><strong>Umqondo ocashile:</strong> a new "
                        "day brings hope and new beginnings.</li><li><strong>Izifengqo:</strong> isenzasamuntu "
                        "(liyamamatheka), isifaniso (linjengomlilo), ukuphindaphinda (ngiyalibona).</li>"
                        "<li><strong>Umoya:</strong> wenjabulo (joyful).</li><li><strong>Ingqikithi:</strong> "
                        "Ubuhle bemvelo nethemba losuku olusha (the beauty of nature and the hope of a new "
                        "day).</li></ul>",
            },
            'video': {'id': 'SbDPnedhev4',
                      'title': 'IsiZulu Poetry: The External Structure Explained (Ukuhluza isakhiwo sangaphandle senkondlo)',
                      'channel': 'Zibula Dladla', 'minutes': 10},
            'worksheet': {
                'instructions': 'Funda inkondlo bese uphendula. Poem: "Imvula" - Imvula iyana, iyana, / '
                                'ihlanza umhlaba owomile. / Izimbali ziyajabula, / zinjengezingane ezidlalayo.',
                'exercises': [
                    '1. Inkondlo inemigqa emingaki? (How many lines?)',
                    '2. What is the umqondo osobala (literal meaning) of the poem?',
                    '3. Name the figure of speech in "Izimbali ziyajabula" and explain it.',
                    '4. Name the figure of speech in "zinjengezingane ezidlalayo".',
                    '5. Why does the poet repeat "iyana"?',
                    '6. Describe the umoya (mood) and give the ingqikithi of the poem.',
                ],
            },
            'quiz': [
                ('mcq', '"Umqondo ocashile" refers to the poem\'s...',
                 ['title', 'hidden / deeper meaning', 'number of lines', 'poet'], 1),
                ('mcq', 'In isiZulu, a stanza is called...', ['isigaba', 'isihloko', 'umoya', 'imbongi'], 0),
                ('tf', '"Umoya" of a poem refers to its mood.', True),
                ('tf', 'The external structure (isakhiwo sangaphandle) is about figures of speech only.', False),
            ],
            'homework': {
                'title': 'Hlaziya inkondlo',
                'instructions': 'Choose an isiZulu poem from your prescribed anthology.',
                'tasks': [
                    'Describe its external structure (stanzas, lines, repetition).',
                    'Explain the umqondo osobala and umqondo ocashile.',
                    'Identify two izifengqo and state the umoya and ingqikithi.',
                ],
                'marks': 15,
            },
        },
        {
            'title': 'Incwadi esemthethweni: writing a formal letter',
            'minutes': 50,
            'objectives': [
                'Ngiyakwazi ukubhala incwadi esemthethweni ngefomethi efanele (correct format).',
                'I can use a formal register and polite requests (Sicela...).',
                'I know the difference between a formal letter and incwadi yobungane (friendly letter).',
            ],
            'notes': "<p>An <strong>incwadi esemthethweni</strong> (formal letter) is written to an official, "
                     "company, principal or newspaper - to complain (<em>isikhalazo</em>), apply "
                     "(<em>isicelo</em>) or request information.</p>"
                     "<ol><li><strong>Ikheli lomlobi</strong> (writer's address) - top right, with the "
                     "<strong>usuku</strong> (date) below it.</li><li><strong>Ikheli lomamukeli</strong> "
                     "(recipient's address) - on the left.</li><li><strong>Isibingelelo</strong> (salutation): "
                     "<em>Mnumzane</em> (Sir) or <em>Nkosikazi</em> (Madam).</li><li><strong>Isihloko</strong> "
                     "(subject line) in capitals: <em>ISIKHALAZO NGOMGWAQO OMUBI</em>.</li>"
                     "<li><strong>Umzimba</strong> (body) - state the reason, give details and make a polite "
                     "request: <em>Sicela ...</em></li><li><strong>Isiphetho</strong> (closing): <em>Ozithobayo,"
                     "</em> (Yours faithfully), signature and full name.</li></ol>"
                     "<p>A friendly letter (<em>incwadi yobungane</em>) starts with <em>Mngane wami "
                     "othandekayo</em> and ends with <em>Yimina umngane wakho</em>; it has only the writer's "
                     "address and an informal tone.</p>",
            'key_terms': [
                ('incwadi esemthethweni', 'formal letter'),
                ('Mnumzane / Nkosikazi', 'Sir / Madam'),
                ('isihloko', 'subject line / heading'),
                ('Ozithobayo', 'Yours faithfully'),
                ('isikhalazo', 'complaint'),
            ],
            'example': {
                'title': 'Isibonelo: umzimba wencwadi yesikhalazo (body of a complaint letter)',
                'html': "<p><em>Mnumzane</em></p><p><strong><em>ISIKHALAZO NGOMGWAQO OMUBI</em></strong></p>"
                        "<p><em>Ngibhala le ncwadi ngikhalaza ngesimo esibi somgwaqo oseduze nesikole sethu. "
                        "Umgwaqo unemigodi eminingi, futhi izingane zisengozini uma zihamba ziya esikoleni.</em>"
                        "</p><p><em>Sicela umasipala alungise lo mgwaqo ngokushesha. Ngiyabonga "
                        "kusengaphambili.</em></p><p><em>Ozithobayo<br>(isiginesha)<br>T. Nkosi</em></p><p>"
                        "English: I am writing to complain about the bad condition of the road near our school. "
                        "The road has many potholes, and children are in danger when they walk to school. We "
                        "ask the municipality to fix this road urgently. Thank you in advance.</p>",
            },
            'video': {'id': 'HZwctI71w4w',
                      'title': 'IPHEPHA LESI-3 : Explained : Incwadi Yasemthethweni: Isikhalazo/Incwadi Yokukhononda Made Easy.',
                      'channel': 'IsiZulu: Grade 12 Intervention', 'minutes': 12},
            'worksheet': {
                'instructions': 'Phendula imibuzo ngencwadi esemthethweni.',
                'exercises': [
                    '1. List the parts of a formal letter in the correct order.',
                    '2. Where is ikheli lomlobi written?',
                    '3. Write a suitable isihloko for a letter applying for a holiday job at a supermarket.',
                    '4. How do you end a formal letter in isiZulu?',
                    '5. Translate: "We ask the principal to open the library after school."',
                    '6. Name two differences between a formal letter and incwadi yobungane.',
                ],
            },
            'quiz': [
                ('mcq', 'How do you end a formal letter in isiZulu?',
                 ['Yimina umngane wakho', 'Ozithobayo', 'Sala kahle', 'Sawubona'], 1),
                ('mcq', 'Which salutation is used in a formal letter to a man?',
                 ['Mngane wami', 'Mnumzane', 'Sawubona baba', 'Nkosikazi'], 1),
                ('tf', 'A formal letter includes both the writer\'s and the recipient\'s addresses.', True),
                ('tf', 'Slang and an informal tone are suitable in incwadi esemthethweni.', False),
            ],
            'homework': {
                'title': 'Bhala incwadi esemthethweni',
                'instructions': 'Write a formal letter (120-150 words) to your principal asking for a study room to be opened during break.',
                'tasks': [
                    'Use the correct format: both addresses, date, isibingelelo, isihloko, umzimba, isiphetho.',
                    'Explain why the study room is needed and make a polite request with "Sicela".',
                    'Close correctly with "Ozithobayo" and your full name.',
                ],
                'marks': 20,
            },
        },
    ],
}

# ---------------------------------------------------------------------------
# LIFE ORIENTATION
# ---------------------------------------------------------------------------

LESSONS[(10, 'LO')] = {
    'topic': 'Development of the self in society: self-awareness, self-esteem and self-development',
    'caps': "Life Orientation Gr 10 Term 1, Topic 1 (CAPS/ATP): Development of the self in society - "
            "strategies to enhance self-awareness, self-esteem and self-development; factors that "
            "influence self-concept formation and self-motivation.",
    'summary': "Learners explore who they are (self-concept and self-awareness), what influences their "
               "self-esteem, and practical strategies to build a healthy sense of self.",
    'days': [
        {
            'title': 'Self-awareness and self-concept: who am I?',
            'minutes': 40,
            'objectives': [
                'Define self-awareness, self-concept and self-image.',
                'Identify my own strengths, weaknesses, values and interests.',
                'Explain how self-awareness helps in making decisions.',
            ],
            'notes': "<p>Grade 10 is a time of change: a new phase, new subjects and new friendships. Knowing "
                     "yourself helps you handle these changes.</p>"
                     "<ul><li><strong>Self-awareness</strong> is the ability to recognise your own feelings, "
                     "thoughts, strengths, weaknesses, values and behaviour, and how they affect others.</li>"
                     "<li><strong>Self-concept</strong> is the overall picture you have of yourself - your "
                     "beliefs about your abilities, personality, roles and appearance ('I am a good friend', "
                     "'I am bad at maths').</li><li><strong>Self-image</strong> is how you see yourself, "
                     "especially your appearance; it may differ from how others see you.</li></ul>"
                     "<p>Your self-concept is formed by <strong>family</strong>, <strong>friends and peers"
                     "</strong>, <strong>teachers</strong>, <strong>culture and religion</strong>, <strong>the "
                     "media</strong>, and your own <strong>experiences</strong> of success and failure.</p>"
                     "<p>A useful tool is a personal <strong>SWOT analysis</strong>: Strengths and Weaknesses "
                     "(internal), Opportunities and Threats (external). Self-awareness helps you choose "
                     "subjects and careers that suit you, resist negative peer pressure, and build healthy "
                     "relationships.</p>",
            'key_terms': [
                ('self-awareness', 'recognising your own feelings, strengths, weaknesses and values'),
                ('self-concept', 'the overall set of beliefs you hold about yourself'),
                ('self-image', 'the mental picture you have of yourself, especially your appearance'),
                ('values', 'beliefs about what is important and right that guide your choices'),
            ],
            'example': {
                'title': 'Class activity: a personal SWOT analysis',
                'html': "<p>Draw a square divided into four blocks. An example for a learner called Ayanda:</p>"
                        "<ul><li><strong>Strengths:</strong> creative, good listener, enjoys languages.</li>"
                        "<li><strong>Weaknesses:</strong> procrastinates, nervous to speak in front of a class."
                        "</li><li><strong>Opportunities:</strong> school debating club, a library close to home."
                        "</li><li><strong>Threats:</strong> too much time on a cellphone, friends who skip "
                        "classes.</li></ul><p>Discuss: How could Ayanda use her strengths and opportunities to "
                        "work on her weaknesses?</p>",
            },
            'video': {'id': 'oxxbx-sS0L4', 'title': 'Self-Awareness, Self-Esteem and Self-Development | Grade 10 | Life Orientation',
                      'channel': 'Coeval College', 'minutes': 10},
            'worksheet': {
                'instructions': 'Answer the questions in full sentences. Be honest - this is about you.',
                'exercises': [
                    '1. Define self-awareness in your own words.',
                    '2. Explain the difference between self-concept and self-image.',
                    '3. List three of your strengths and two weaknesses.',
                    '4. Name three factors that influence a teenager\'s self-concept and explain one.',
                    '5. Complete a personal SWOT analysis (two points per block).',
                    '6. Explain how self-awareness can help you resist negative peer pressure.',
                ],
            },
            'quiz': [
                ('mcq', 'The overall set of beliefs you have about yourself is your...',
                 ['self-concept', 'peer group', 'career', 'environment'], 0),
                ('mcq', 'In a SWOT analysis, the "O" stands for...',
                 ['Objectives', 'Opinions', 'Opportunities', 'Obstacles'], 2),
                ('tf', 'Family, friends and the media can all influence your self-concept.', True),
                ('tf', 'Self-awareness means only knowing your strengths, not your weaknesses.', False),
            ],
            'homework': {
                'title': '"Who am I?" profile',
                'instructions': 'Create a one-page profile of yourself.',
                'tasks': [
                    'List your interests, values, strengths and weaknesses.',
                    'Ask a trusted family member to name two of your strengths; compare with your list.',
                    'Write a short paragraph on what you learnt about yourself.',
                ],
                'marks': 10,
            },
        },
        {
            'title': 'Self-esteem: what shapes how I value myself',
            'minutes': 40,
            'objectives': [
                'Define self-esteem and distinguish between high and low self-esteem.',
                'Identify factors that build or damage self-esteem.',
                'Explain the effect of self-esteem on behaviour, relationships and achievement.',
            ],
            'notes': "<p><strong>Self-esteem</strong> is how much you value, respect and accept yourself. "
                     "Self-concept is <em>what</em> you think about yourself; self-esteem is <em>how you feel"
                     "</em> about it.</p>"
                     "<p><strong>Signs of healthy (high) self-esteem</strong>: you accept compliments and "
                     "criticism, try new things, set goals, are assertive, and do not need others' approval "
                     "all the time.</p>"
                     "<p><strong>Signs of low self-esteem</strong>: negative self-talk ('I'm useless'), fear of "
                     "failure, giving in to peer pressure, comparing yourself to others, and avoiding "
                     "challenges.</p>"
                     "<p><strong>Factors that influence self-esteem</strong></p><ul><li>Support and praise (or "
                     "criticism and abuse) from family.</li><li>Acceptance or rejection by peers; bullying and "
                     "cyber-bullying.</li><li>Social media and unrealistic body images.</li><li>Success and "
                     "failure at school, sport or other activities.</li><li>Your own thoughts and self-talk."
                     "</li></ul><p>Low self-esteem can lead to risky behaviour, poor relationships and poor "
                     "performance. Healthy self-esteem is not arrogance - it is a balanced, realistic respect "
                     "for yourself.</p>",
            'key_terms': [
                ('self-esteem', 'how much you value, respect and accept yourself'),
                ('self-talk', 'the inner voice and thoughts you have about yourself'),
                ('assertive', 'expressing your views and needs confidently while respecting others'),
                ('peer pressure', 'influence from people your own age to behave in a certain way'),
            ],
            'example': {
                'title': 'Case study discussion',
                'html': "<p><strong>Case:</strong> Kagiso posts a photo online. A few classmates leave unkind "
                        "comments about his appearance. He deletes the photo, stops answering questions in "
                        "class and tells himself, 'Everyone thinks I'm a joke.'</p><ol><li>Which factor is "
                        "affecting Kagiso's self-esteem? (peer rejection / cyber-bullying)</li><li>Which signs "
                        "of low self-esteem does he show? (withdrawal, negative self-talk)</li><li>What could "
                        "he do? (talk to a trusted adult, report the comments, focus on supportive friends, "
                        "replace negative self-talk with realistic statements)</li></ol>",
            },
            'video': {'id': 'wC9S_fFMnaU', 'title': 'Self-Esteem', 'channel': 'The School of Life', 'minutes': 5},
            'worksheet': {
                'instructions': 'Answer in full sentences.',
                'exercises': [
                    '1. Define self-esteem and explain how it differs from self-concept.',
                    '2. List three signs of healthy self-esteem.',
                    '3. List three signs of low self-esteem.',
                    '4. Explain how social media can affect a teenager\'s self-esteem.',
                    '5. Why is healthy self-esteem not the same as arrogance?',
                    '6. Describe how low self-esteem could make someone more vulnerable to peer pressure.',
                ],
            },
            'quiz': [
                ('mcq', 'Which is a sign of healthy self-esteem?',
                 ['Constantly comparing yourself to others', 'Avoiding all challenges',
                  'Being able to accept constructive criticism', 'Needing approval for every decision'], 2),
                ('tf', 'Negative self-talk can lower self-esteem.', True),
                ('mcq', 'Self-esteem is best described as...',
                 ['how much you value and accept yourself', 'how much money you have',
                  'the marks you get', 'how many friends you have online'], 0),
                ('tf', 'Healthy self-esteem means believing you are better than everyone else.', False),
            ],
            'homework': {
                'title': 'Self-esteem reflection',
                'instructions': 'Reflect privately on your own self-esteem.',
                'tasks': [
                    'Write down three negative things you sometimes say to yourself.',
                    'Rewrite each as a realistic, positive statement.',
                    'Write a paragraph about one person or experience that has built your self-esteem.',
                ],
                'marks': 10,
            },
        },
        {
            'title': 'Strategies to enhance self-esteem and self-development',
            'minutes': 40,
            'objectives': [
                'Describe practical strategies to build self-esteem.',
                'Explain how self-motivation contributes to self-development.',
                'Create a personal self-development plan.',
            ],
            'notes': "<p><strong>Self-development</strong> is the ongoing process of improving your knowledge, "
                     "skills and character. It builds self-esteem because you see yourself growing.</p>"
                     "<p><strong>Strategies to enhance self-esteem</strong></p><ul><li><strong>Positive, "
                     "realistic self-talk</strong> - challenge 'I always fail' with 'I struggled this time; I "
                     "can prepare better.'</li><li><strong>Set small, achievable goals</strong> - each success "
                     "builds confidence.</li><li><strong>Focus on strengths</strong> and accept that everyone "
                     "has weaknesses.</li><li><strong>Look after your body</strong> - sleep, exercise and "
                     "healthy food affect mood.</li><li><strong>Choose supportive friends</strong> and limit "
                     "time with people or online spaces that make you feel worthless.</li><li><strong>Help "
                     "others</strong> - volunteering gives a sense of purpose.</li><li><strong>Ask for help"
                     "</strong> from a teacher, counsellor or helpline when you need it.</li></ul>"
                     "<p><strong>Self-motivation</strong> is the inner drive to act without someone pushing "
                     "you. <em>Intrinsic</em> motivation comes from inside (enjoyment, pride); <em>extrinsic"
                     "</em> motivation comes from outside rewards (marks, money, praise). Intrinsic motivation "
                     "usually lasts longer.</p>",
            'key_terms': [
                ('self-development', 'the continuous process of improving your skills, knowledge and character'),
                ('self-motivation', 'the inner drive to take action and keep going'),
                ('intrinsic motivation', 'motivation that comes from inside, e.g. enjoyment or pride'),
                ('extrinsic motivation', 'motivation from outside rewards such as marks or praise'),
            ],
            'example': {
                'title': 'Worked example: a self-development plan',
                'html': "<p><strong>Area to develop:</strong> speaking confidently in class.</p><ul><li><strong>"
                        "Why:</strong> I want to take part in debates and oral assessments.</li><li><strong>Step "
                        "1:</strong> answer one question in class each week.</li><li><strong>Step 2:</strong> "
                        "practise my oral at home in front of a mirror or family.</li><li><strong>Step 3:</strong>"
                        " join the debating club by the end of Term 1.</li><li><strong>Support:</strong> my "
                        "English teacher and a friend.</li><li><strong>Self-talk:</strong> 'I am nervous, but I "
                        "am prepared and I can do this.'</li></ul>",
            },
            'video': {'id': 'J0HPVEsnOoI', 'title': 'Ways to Improve Your Self-Esteem',
                      'channel': 'Mind, the mental health charity', 'minutes': 4},
            'worksheet': {
                'instructions': 'Answer the questions and complete the plan.',
                'exercises': [
                    '1. Explain the term "self-development".',
                    '2. Name four strategies to enhance self-esteem.',
                    '3. Distinguish between intrinsic and extrinsic motivation, with one example each.',
                    '4. Rewrite this negative statement positively: "I will never be good at sport."',
                    '5. Choose one area you want to develop this year and explain why.',
                    '6. Write three steps you will take, and name one person who can support you.',
                ],
            },
            'quiz': [
                ('mcq', 'Which is an example of intrinsic motivation?',
                 ['Studying to get a cash reward', 'Reading because you enjoy it',
                  'Cleaning your room to avoid punishment', 'Training only to win a trophy'], 1),
                ('tf', 'Setting small, achievable goals can help build self-esteem.', True),
                ('mcq', 'Which strategy is LEAST likely to improve self-esteem?',
                 ['Positive self-talk', 'Helping others', 'Constantly comparing yourself to influencers',
                  'Getting enough sleep'], 2),
                ('tf', 'Asking a counsellor for help is a sign of weakness.', False),
            ],
            'homework': {
                'title': 'My self-development plan',
                'instructions': 'Complete a personal self-development plan for Term 1.',
                'tasks': [
                    'Name the area you want to develop and why it matters to you.',
                    'Write at least three concrete steps with dates.',
                    'List your support people and one positive self-talk statement.',
                ],
                'marks': 15,
            },
        },
    ],
}

LESSONS[(11, 'LO')] = {
    'topic': 'Development of the self in society: plan and achieve life goals',
    'caps': "Life Orientation Gr 11 Term 1, Topic 1 (CAPS/ATP): Development of the self in society - "
            "plan and achieve life goals: types of goals (short-, medium- and long-term), SMART goals, "
            "steps in goal-setting, problem-solving skills and overcoming obstacles.",
    'summary': "Learners distinguish between types of goals in different areas of life, learn to write SMART "
               "goals, and turn a goal into an action plan that anticipates obstacles.",
    'days': [
        {
            'title': 'Life goals: why they matter and the types of goals',
            'minutes': 40,
            'objectives': [
                'Explain what a life goal is and why goal-setting is important.',
                'Distinguish between short-, medium- and long-term goals.',
                'Identify goals in different areas of life (personal, academic, career, health, financial, social).',
            ],
            'notes': "<p>A <strong>goal</strong> is a specific result you want to achieve and are willing to "
                     "work for. Without goals, it is easy to drift; with goals, you have direction, "
                     "motivation and a way to measure progress.</p>"
                     "<p><strong>Types of goals by time</strong></p><ul><li><strong>Short-term</strong> - "
                     "days to a few months (e.g. finish a project this week, pass the March test).</li>"
                     "<li><strong>Medium-term</strong> - several months to about two years (e.g. pass Grade "
                     "11 with an average of 65%).</li><li><strong>Long-term</strong> - several years (e.g. "
                     "qualify as an electrician, start a business).</li></ul>"
                     "<p>Short-term goals are the <em>stepping stones</em> to long-term goals.</p>"
                     "<p><strong>Areas of life</strong>: personal, academic, career, health and fitness, "
                     "financial, social/relationships, and spiritual. A balanced life has goals in more than "
                     "one area.</p>"
                     "<p>Your <strong>values</strong> (what is important to you) should guide your goals. "
                     "Goals that match your values motivate you; goals set only to please others are hard to "
                     "keep.</p>",
            'key_terms': [
                ('goal', 'a specific result you plan and work to achieve'),
                ('short-term goal', 'a goal achievable in days to a few months'),
                ('medium-term goal', 'a goal achievable in several months to about two years'),
                ('long-term goal', 'a goal that takes several years to achieve'),
            ],
            'example': {
                'title': 'Class activity: building a goal ladder',
                'html': "<p><strong>Long-term goal:</strong> become a registered nurse.</p><ul><li><strong>"
                        "Medium-term:</strong> pass matric with a bachelor's pass, including Life Sciences.</li>"
                        "<li><strong>Short-term:</strong> score at least 60% in the Grade 11 Term 1 Life "
                        "Sciences test.</li><li><strong>This week:</strong> make summaries of chapter 1 and do "
                        "the textbook exercises.</li></ul><p>Discuss: Which area(s) of life does this goal "
                        "belong to? (career, academic) What values might sit behind it? (caring for others, "
                        "security)</p>",
            },
            'video': {'id': '6PakZMnf8Vg', 'title': 'Goal-Setting, Problem-Solving and Values | Grade 11 | Life Orientation',
                      'channel': 'Coeval College', 'minutes': 10},
            'worksheet': {
                'instructions': 'Answer the questions in full sentences.',
                'exercises': [
                    '1. Define a goal and give two reasons why goal-setting is important.',
                    '2. Classify as short-, medium- or long-term: (a) save R200 this month (b) get a degree (c) pass Grade 11.',
                    '3. Name five areas of life in which a person can set goals.',
                    '4. Explain how short-term goals help you reach long-term goals.',
                    '5. Why should your goals be based on your own values?',
                    '6. Write one goal of your own for three different areas of life.',
                ],
            },
            'quiz': [
                ('mcq', '"Pass this Friday\'s Maths test" is an example of a...',
                 ['long-term goal', 'short-term goal', 'medium-term goal', 'value'], 1),
                ('tf', 'Short-term goals can be stepping stones towards long-term goals.', True),
                ('mcq', '"Qualify as an engineer" is best classified as a...',
                 ['short-term goal', 'daily task', 'long-term goal', 'habit'], 2),
                ('tf', 'Goals set only to please other people are usually the easiest to keep.', False),
            ],
            'homework': {
                'title': 'My goal ladder',
                'instructions': 'Draw a goal ladder for one long-term goal of your own.',
                'tasks': [
                    'Write your long-term goal at the top.',
                    'Add one medium-term and two short-term goals that lead to it.',
                    'Write two sentences explaining which of your values this goal reflects.',
                ],
                'marks': 10,
            },
        },
        {
            'title': 'Writing SMART goals',
            'minutes': 40,
            'objectives': [
                'Explain each element of a SMART goal.',
                'Evaluate whether a goal is SMART.',
                'Rewrite vague goals as SMART goals.',
            ],
            'notes': "<p>Vague goals such as 'I want to do better at school' are hard to achieve because you "
                     "cannot tell when you have reached them. Use the <strong>SMART</strong> test:</p>"
                     "<ul><li><strong>S - Specific</strong>: clearly state what you want. <em>Improve my "
                     "Mathematics mark.</em></li><li><strong>M - Measurable</strong>: how will you know you "
                     "have achieved it? <em>From 48% to 60%.</em></li><li><strong>A - Achievable</strong>: it "
                     "should stretch you but be possible with the time and resources you have.</li>"
                     "<li><strong>R - Realistic / Relevant</strong>: it fits your situation and matters to "
                     "your bigger goals.</li><li><strong>T - Time-bound</strong>: it has a deadline. <em>By the "
                     "end of Term 1.</em></li></ul>"
                     "<p><strong>SMART version:</strong> 'I will raise my Mathematics mark from 48% to 60% by "
                     "the end of Term 1 by doing 30 minutes of extra exercises every weekday.'</p>"
                     "<p>Write goals in the positive ('I will...') and in the first person. Writing a goal down "
                     "and sharing it with someone you trust increases commitment.</p>",
            'key_terms': [
                ('specific', 'clearly defined, not vague'),
                ('measurable', 'progress can be tracked or counted'),
                ('achievable', 'possible with the time, skills and resources available'),
                ('time-bound', 'has a clear deadline'),
            ],
            'example': {
                'title': 'Worked example: from vague to SMART',
                'html': "<p><strong>Vague:</strong> 'I want to get fit.'</p><ul><li>Specific: run 5 km "
                        "without stopping.</li><li>Measurable: time each run and record the distance.</li>"
                        "<li>Achievable: I can already run 2 km; I will increase slowly.</li><li>Relevant: I "
                        "want to try out for the athletics team.</li><li>Time-bound: by 31 March.</li></ul><p>"
                        "<strong>SMART goal:</strong> 'I will be able to run 5 km without stopping by 31 March "
                        "by jogging three times a week and adding 500 m every two weeks.'</p>",
            },
            'video': {'id': 'i0QfCZjASX8', 'title': 'How to Set SMART Goals | Goal Setting for Students',
                      'channel': '2 Minute Classroom', 'minutes': 3},
            'worksheet': {
                'instructions': 'Apply the SMART test.',
                'exercises': [
                    '1. Write out what each letter of SMART stands for.',
                    '2. Is this goal SMART? "I want to read more." Explain.',
                    '3. Which SMART element is missing: "I will save R500 for a new phone."?',
                    '4. Rewrite as a SMART goal: "I want to be better at English."',
                    '5. Rewrite as a SMART goal: "I want to spend less time on my phone."',
                    '6. Write one SMART academic goal for this term.',
                ],
            },
            'quiz': [
                ('mcq', 'In SMART, the "T" stands for...', ['Talented', 'Time-bound', 'Tested', 'Typical'], 1),
                ('mcq', 'Which goal is the most SMART?',
                 ['I want to do well.', 'I will study more.',
                  'I will improve my History mark from 55% to 65% by June by studying 4 hours a week.',
                  'I hope to pass.'], 2),
                ('tf', '"I will save R300 by 30 April" is measurable and time-bound.', True),
                ('tf', 'A SMART goal should be as vague as possible so that you cannot fail.', False),
            ],
            'homework': {
                'title': 'Three SMART goals',
                'instructions': 'Write three SMART goals for 2026.',
                'tasks': [
                    'Write one academic, one health and one personal SMART goal.',
                    'Under each, show how it meets every SMART element.',
                    'Share one goal with a family member and ask them to sign as a witness.',
                ],
                'marks': 15,
            },
        },
        {
            'title': 'From goal to action: action plans, obstacles and problem-solving',
            'minutes': 40,
            'objectives': [
                'Draw up an action plan with steps, resources and deadlines.',
                'Identify possible obstacles and plan ways to overcome them.',
                'Apply problem-solving steps when a plan does not work.',
            ],
            'notes': "<p>A goal without a plan is only a wish. An <strong>action plan</strong> breaks a goal "
                     "into steps.</p>"
                     "<ol><li>State your SMART goal.</li><li>List the <strong>steps</strong> you need to take, "
                     "in order.</li><li>Identify <strong>resources</strong> and <strong>support</strong> "
                     "(people, money, time, materials).</li><li>Set <strong>deadlines</strong> for each step."
                     "</li><li>Identify possible <strong>obstacles</strong> and plan how to overcome them.</li>"
                     "<li><strong>Monitor</strong> progress (e.g. a weekly check) and <strong>reward</strong> "
                     "yourself for milestones.</li></ol>"
                     "<p><strong>Common obstacles</strong>: procrastination, lack of money or resources, "
                     "negative peer pressure, illness, family responsibilities, and fear of failure.</p>"
                     "<p><strong>Problem-solving steps</strong> when things go wrong: (1) identify the problem; "
                     "(2) brainstorm possible solutions; (3) weigh the pros and cons; (4) choose and apply the "
                     "best solution; (5) evaluate the result and adjust. A setback does not mean failure - "
                     "<em>adjust the plan, not the goal</em> (unless the goal is no longer realistic).</p>",
            'key_terms': [
                ('action plan', 'a list of steps, resources and deadlines for achieving a goal'),
                ('obstacle', 'something that blocks or slows progress towards a goal'),
                ('milestone', 'an important point of progress along the way to a goal'),
                ('procrastination', 'delaying tasks that should be done now'),
            ],
            'example': {
                'title': 'Worked example: an action plan',
                'html': "<p><strong>SMART goal:</strong> raise my Accounting mark from 50% to 62% by the end of "
                        "Term 1.</p><ul><li><strong>Steps:</strong> (1) redo all class exercises each "
                        "afternoon; (2) attend Thursday extra classes; (3) do one past paper every two weeks."
                        "</li><li><strong>Resources:</strong> textbook, past papers, teacher, study partner.</li>"
                        "<li><strong>Obstacle:</strong> I look after my younger sister after school. "
                        "<strong>Solution:</strong> study while she does her homework; use weekends for past "
                        "papers.</li><li><strong>Monitor:</strong> record my marks in a table each week.</li>"
                        "<li><strong>Reward:</strong> a movie night after the March test.</li></ul>",
            },
            'video': {'id': 'PCRSVRD2EAk', 'title': 'Setting SMART Goals - How To Properly Set a Goal (animated)',
                      'channel': 'Better Than Yesterday', 'minutes': 8},
            'worksheet': {
                'instructions': 'Use one of your SMART goals from yesterday.',
                'exercises': [
                    '1. Write your SMART goal.',
                    '2. List at least four steps in order, each with a deadline.',
                    '3. List the resources and people who can support you.',
                    '4. Identify two possible obstacles and a solution for each.',
                    '5. Explain the five problem-solving steps in your own words.',
                    '6. How will you monitor your progress and reward yourself?',
                ],
            },
            'quiz': [
                ('mcq', 'What is the FIRST step of problem-solving?',
                 ['Choose a solution', 'Identify the problem', 'Evaluate the result', 'Reward yourself'], 1),
                ('tf', 'Monitoring progress regularly helps you stay on track with a goal.', True),
                ('mcq', 'Delaying a task that should be done now is called...',
                 ['motivation', 'procrastination', 'a milestone', 'a resource'], 1),
                ('tf', 'If one step of your plan fails, you must always give up the goal.', False),
            ],
            'homework': {
                'title': 'Complete action plan',
                'instructions': 'Write a complete action plan for one of your SMART goals.',
                'tasks': [
                    'Present your plan as a table: step, deadline, resources, possible obstacle, solution.',
                    'Include a monitoring method and a reward.',
                    'Write a short reflection: what is the biggest obstacle for you and how will you handle it?',
                ],
                'marks': 15,
            },
        },
    ],
}

LESSONS[(12, 'LO')] = {
    'topic': 'Development of the self in society: life skills to adapt to change - stress and conflict management',
    'caps': "Life Orientation Gr 12 Term 1, Topic 1 (CAPS/ATP): Development of the self in society - life "
            "skills required to adapt to change as part of ongoing healthy lifestyle choices: stress "
            "management (causes, symptoms, strategies) and conflict resolution.",
    'summary': "Matric learners identify the causes and signs of stress, practise healthy stress-management "
               "strategies for a demanding year, and learn styles and steps for resolving conflict.",
    'days': [
        {
            'title': 'Understanding stress: stressors, signs and effects',
            'minutes': 40,
            'objectives': [
                'Define stress and distinguish between eustress and distress.',
                'Identify common stressors for Grade 12 learners.',
                'Recognise the physical, emotional and behavioural signs of stress.',
            ],
            'notes': "<p><strong>Stress</strong> is the body's and mind's response to a demand or threat "
                     "(a <em>stressor</em>). When you face a stressor, the body releases hormones such as "
                     "<em>adrenaline</em> and <em>cortisol</em> - the <strong>fight-or-flight response</strong>"
                     ": your heart beats faster and your muscles tense.</p>"
                     "<ul><li><strong>Eustress</strong> - positive stress that motivates you (e.g. excitement "
                     "before a match or a manageable deadline).</li><li><strong>Distress</strong> - negative "
                     "stress that overwhelms you, especially when it lasts a long time (chronic stress).</li>"
                     "</ul><p><strong>Common stressors in matric</strong>: exams and deadlines, decisions about "
                     "further study and careers, finances, family problems, relationships, peer pressure, "
                     "social media and major life changes.</p>"
                     "<p><strong>Signs of stress</strong></p><ul><li><em>Physical</em>: headaches, tiredness, "
                     "sleep problems, stomach upsets, frequent illness.</li><li><em>Emotional</em>: anxiety, "
                     "irritability, mood swings, feeling overwhelmed.</li><li><em>Behavioural</em>: "
                     "procrastination, withdrawal from friends, changes in eating, substance use.</li>"
                     "<li><em>Cognitive</em>: poor concentration, forgetfulness, negative thinking.</li></ul>"
                     "<p>Long-term distress can harm health, relationships and results, so it is important to "
                     "recognise it early.</p>",
            'key_terms': [
                ('stress', "the body's and mind's response to a demand or threat"),
                ('stressor', 'an event or situation that causes stress'),
                ('eustress', 'positive stress that motivates and energises'),
                ('distress', 'negative stress that overwhelms and harms well-being'),
                ('fight-or-flight response', 'the automatic physical reaction of the body to a threat'),
            ],
            'example': {
                'title': 'Class activity: stress inventory',
                'html': "<p>In pairs, sort these situations into <strong>eustress</strong> or "
                        "<strong>distress</strong> and discuss why:</p><ol><li>Preparing for a debate final you "
                        "feel ready for. (eustress)</li><li>Weeks of arguing at home with no sleep. (distress)"
                        "</li><li>Starting a part-time job you chose. (often eustress)</li><li>Five assignments "
                        "due on the same day with no plan. (distress)</li></ol><p>Then list three signs you "
                        "notice in yourself when stressed - physical, emotional and behavioural.</p>",
            },
            'video': {'id': '2CemW_zovFE', 'title': 'Life Orientation Grade 12: What Is Stress? [Comprehensive Guide]',
                      'channel': 'Ace My Exams ', 'minutes': 10},
            'worksheet': {
                'instructions': 'Answer the questions in full sentences.',
                'exercises': [
                    '1. Define stress and stressor.',
                    '2. Distinguish between eustress and distress, with an example of each.',
                    '3. Describe the fight-or-flight response.',
                    '4. List five stressors that Grade 12 learners commonly face.',
                    '5. Give two physical, two emotional and two behavioural signs of stress.',
                    '6. Explain two ways in which chronic stress can affect a learner\'s performance.',
                ],
            },
            'quiz': [
                ('mcq', 'Positive stress that motivates you is called...',
                 ['distress', 'eustress', 'burnout', 'anxiety disorder'], 1),
                ('mcq', 'Which is a behavioural sign of stress?',
                 ['Headaches', 'Withdrawing from friends', 'Increased heart rate', 'Muscle tension'], 1),
                ('tf', 'Adrenaline is released during the fight-or-flight response.', True),
                ('tf', 'All stress is harmful and should be avoided completely.', False),
            ],
            'homework': {
                'title': 'Stress diary',
                'instructions': 'Keep a stress diary for three days.',
                'tasks': [
                    'Record each stressful situation, the time and how you reacted.',
                    'Label each as eustress or distress.',
                    'Write a paragraph identifying your main stressors and your typical signs of stress.',
                ],
                'marks': 10,
            },
        },
        {
            'title': 'Managing stress: healthy coping strategies',
            'minutes': 40,
            'objectives': [
                'Distinguish between healthy and unhealthy ways of coping with stress.',
                'Apply practical stress-management strategies, including time management.',
                'Know where to find help when stress becomes overwhelming.',
            ],
            'notes': "<p><strong>Stress management</strong> means reducing stressors where possible and "
                     "handling the rest in healthy ways.</p>"
                     "<p><strong>Healthy strategies</strong></p><ul><li><strong>Time management</strong> - use a "
                     "study timetable, break big tasks into small ones, prioritise (urgent vs important), "
                     "and avoid leaving work until the last minute.</li><li><strong>Physical activity</strong> "
                     "- exercise releases endorphins that improve mood.</li><li><strong>Sleep and nutrition"
                     "</strong> - 8-9 hours of sleep, regular meals and enough water.</li><li><strong>"
                     "Relaxation</strong> - deep breathing (breathe in for 4, hold for 4, out for 4), "
                     "stretching, prayer or meditation, music, hobbies.</li><li><strong>Positive thinking"
                     "</strong> - challenge catastrophic thoughts ('If I fail this test my life is over').</li>"
                     "<li><strong>Talk to someone</strong> - friends, family, a teacher or counsellor.</li>"
                     "<li><strong>Set boundaries</strong> - say no to extra demands when you are overloaded, "
                     "and limit social media.</li></ul>"
                     "<p><strong>Unhealthy coping</strong> such as alcohol, drugs, overeating, isolation or "
                     "aggression may feel like relief but makes stress worse over time.</p>"
                     "<p>If stress feels unmanageable, get help: a school counsellor, a clinic, or a support "
                     "organisation such as SADAG (the South African Depression and Anxiety Group).</p>",
            'key_terms': [
                ('stress management', 'techniques to reduce and cope with stress in healthy ways'),
                ('time management', 'planning and controlling how you use your time'),
                ('endorphins', 'chemicals released during exercise that improve mood'),
                ('coping strategy', 'a way of dealing with a difficult situation'),
            ],
            'example': {
                'title': 'Worked example: a study-week plan to reduce stress',
                'html': "<p><strong>Situation:</strong> Nomsa has a Life Sciences test on Friday, an English "
                        "essay due Thursday and netball practice on Tuesday.</p><ul><li><strong>Monday:</strong> "
                        "plan the essay (30 min); Life Sciences summaries chapter 1 (45 min).</li><li><strong>"
                        "Tuesday:</strong> netball (exercise counts!); write the essay draft (45 min).</li>"
                        "<li><strong>Wednesday:</strong> edit the essay; Life Sciences practice questions.</li>"
                        "<li><strong>Thursday:</strong> hand in the essay; revise with a study partner.</li>"
                        "<li><strong>Every night:</strong> phone off at 21:30, sleep by 22:00.</li></ul><p>"
                        "Breaking tasks down turns one big, stressful load into manageable steps.</p>",
            },
            'video': {'id': 'TAZL5qRnvwk', 'title': 'Stress Management | Grade 12 | Life Orientation',
                      'channel': 'Coeval College', 'minutes': 10},
            'worksheet': {
                'instructions': 'Answer the questions and complete the plan.',
                'exercises': [
                    '1. List five healthy stress-management strategies.',
                    '2. Explain why using alcohol to cope with stress is harmful.',
                    '3. Describe the 4-4-4 breathing technique.',
                    '4. Explain two time-management techniques that help learners.',
                    '5. Rewrite this catastrophic thought realistically: "If I fail this test, I will never get into university."',
                    '6. Name two places or people a learner can go to for help with stress.',
                ],
            },
            'quiz': [
                ('mcq', 'Which is a HEALTHY way to cope with stress?',
                 ['Using alcohol to relax', 'Isolating yourself', 'Regular physical exercise',
                  'Skipping meals to study more'], 2),
                ('tf', 'Breaking a big task into smaller steps can reduce stress.', True),
                ('mcq', 'Chemicals released during exercise that improve mood are called...',
                 ['endorphins', 'cortisol', 'stressors', 'vitamins'], 0),
                ('tf', 'Unhealthy coping strategies reduce stress permanently.', False),
            ],
            'homework': {
                'title': 'Personal stress-management plan',
                'instructions': 'Use your stress diary to create a personal plan.',
                'tasks': [
                    'Identify your three biggest stressors.',
                    'For each, write two healthy strategies you will use.',
                    'Draw up a weekly timetable that includes study, exercise, rest and sleep.',
                ],
                'marks': 15,
            },
        },
        {
            'title': 'Conflict: causes, styles and resolution skills',
            'minutes': 40,
            'objectives': [
                'Identify common causes of conflict.',
                'Describe the five conflict-handling styles.',
                'Apply the steps of conflict resolution using "I"-messages and active listening.',
            ],
            'notes': "<p><strong>Conflict</strong> is a disagreement between people with different needs, "
                     "values, opinions or goals. It is a normal part of life; what matters is how we handle "
                     "it. Unresolved conflict is a major source of stress.</p>"
                     "<p><strong>Causes</strong>: poor communication, misunderstandings, different values or "
                     "beliefs, competition for resources, jealousy, unmet expectations, prejudice.</p>"
                     "<p><strong>Five conflict styles</strong></p><ul><li><strong>Avoiding</strong> - ignoring "
                     "the conflict (lose-lose).</li><li><strong>Accommodating</strong> - giving in to keep the "
                     "peace (lose-win).</li><li><strong>Competing</strong> - insisting on your own way "
                     "(win-lose).</li><li><strong>Compromising</strong> - each side gives up something.</li>"
                     "<li><strong>Collaborating</strong> - working together to find a solution that meets both "
                     "sides' needs (win-win).</li></ul>"
                     "<p><strong>Steps to resolve conflict</strong>: (1) calm down and choose a good time; (2) "
                     "each person explains their view using <strong>'I'-messages</strong> ('I feel hurt when "
                     "plans change without telling me') rather than blaming 'you'-messages; (3) "
                     "<strong>listen actively</strong> - make eye contact, do not interrupt, summarise what "
                     "you heard; (4) identify the real problem; (5) brainstorm solutions; (6) agree on a "
                     "solution and follow up. If you cannot resolve it, ask a neutral third person to "
                     "<strong>mediate</strong>.</p>",
            'key_terms': [
                ('conflict', 'a disagreement between people with different needs, values or goals'),
                ('collaborating', 'working together to find a win-win solution'),
                ("'I'-message", 'a statement of your feelings and needs without blaming the other person'),
                ('active listening', 'fully concentrating on, understanding and responding to a speaker'),
                ('mediation', 'a neutral third party helps people in conflict reach an agreement'),
            ],
            'example': {
                'title': 'Role-play: resolving a group-project conflict',
                'html': "<p><strong>Situation:</strong> Thabo has not done his part of a group project due "
                        "Friday. Lindiwe is angry.</p><p><strong>Blaming 'you'-message:</strong> 'You are so "
                        "lazy, you always let us down!'</p><p><strong>'I'-message:</strong> 'I feel worried "
                        "when your section isn't done, because our whole group mark depends on it.'</p><p>"
                        "<strong>Active listening:</strong> Thabo explains he has been working night shifts at "
                        "a shop. Lindiwe summarises: 'So you've had no time after school.'</p><p><strong>"
                        "Collaborative solution:</strong> Thabo does the research during break; Lindiwe types "
                        "it up. Both needs are met (win-win).</p>",
            },
            'video': {'id': 'gu8gSuF_lvw', 'title': 'Fighting Fair: How Do You Resolve Conflict?',
                      'channel': 'AMAZE Org', 'minutes': 3},
            'worksheet': {
                'instructions': 'Answer the questions in full sentences.',
                'exercises': [
                    '1. Define conflict and name four common causes.',
                    '2. Describe the five conflict-handling styles and say which leads to a win-win outcome.',
                    '3. Change this into an "I"-message: "You never listen to me!"',
                    '4. List three things you do when you listen actively.',
                    '5. Explain the role of a mediator in conflict resolution.',
                    '6. Describe a conflict you have seen and explain how it could have been resolved using the steps.',
                ],
            },
            'quiz': [
                ('mcq', 'Which conflict style aims for a win-win solution?',
                 ['Avoiding', 'Competing', 'Accommodating', 'Collaborating'], 3),
                ('mcq', 'Which is an "I"-message?',
                 ['You always ruin everything.', 'I feel frustrated when I am interrupted.',
                  'You are so selfish.', 'Why can\'t you ever be on time?'], 1),
                ('tf', 'Active listening includes not interrupting the speaker.', True),
                ('tf', 'Avoiding a conflict always solves the problem permanently.', False),
                ('mcq', 'A neutral person who helps two sides reach agreement is a...',
                 ['mediator', 'competitor', 'stressor', 'bystander'], 0),
            ],
            'homework': {
                'title': 'Conflict-resolution scenario',
                'instructions': 'Write a short dialogue showing a conflict being resolved well.',
                'tasks': [
                    'Choose a realistic conflict (home, school, friends or work).',
                    'Write a dialogue of 10-14 lines that uses at least two "I"-messages and active listening.',
                    'End with a collaborative solution and explain in two sentences why it is win-win.',
                ],
                'marks': 15,
            },
        },
    ],
}
