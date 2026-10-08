"""FET humanities and commerce — Term 1, Week 1 demo lessons (Grades 10–12).

Offerings (15): grades 10, 11 and 12 x
    HIST (History), GEOG (Geography), ACC (Accounting),
    BUS-STUD (Business Studies), ECON (Economics).

Week 1 = the first topic of each subject's CAPS Term 1 teaching plan:
    HIST      Gr10 The world around 1600 | Gr11 Communism in Russia 1900-1940 |
              Gr12 The Cold War: origins
    GEOG      Gr10 The atmosphere | Gr11 Energy balance & global air circulation |
              Gr12 Mid-latitude cyclones
    ACC       Gr10 Concepts, GAAP & the accounting equation | Gr11 Bank reconciliation |
              Gr12 Companies: concepts, ledger accounts & notes
    BUS-STUD  Gr10 Micro, market and macro environments | Gr11 Influences on business
              environments | Gr12 Impact of recent legislation
    ECON      Gr10 Basic concepts: the economic problem | Gr11 Factors of production |
              Gr12 Circular flow

Sources: DBE CAPS FET (Grades 10-12) policy statements for History, Geography,
Accounting, Business Studies and Economics; DBE Annual Teaching Plans (ATP) Term 1;
WCED ePortal Term 1 Week 1 lesson series (e.g. "Accounting Gr 11 T1 W1 bank
reconciliation", "Gr 12 Accounting T1 W1 company accounts", "Economics Gr 11 T1 W1
factors of production", "Economics Gr 12 T1 W1 circular flow").
"""

LESSONS = {
    # ------------------------------------------------------------------ HISTORY
    (10, 'HIST'): {
        'topic': 'The world around 1600',
        'caps': 'History Grade 10, Term 1, Topic 1: The world around 1600 — Ming China, the Songhai '
                'Empire, Mughal India and the Ottoman Empire; their power, wealth, trade and '
                'achievements before European expansion',
        'summary': 'Learners meet four great societies of the world around 1600 and ask how they '
                   'organised power, wealth and knowledge before European expansion changed the '
                   'balance of the world.',
        'days': [
            {
                'title': 'Ming China: a powerful empire around 1600',
                'minutes': 45,
                'objectives': [
                    'Learners will explain why historians study the world "around 1600".',
                    'Learners will describe how the Ming emperors ruled China.',
                    'Learners will identify Ming achievements in trade, technology and culture.',
                    'Learners will explain the purpose and significance of Zheng He\'s voyages.',
                ],
                'notes': (
                    '<p>Around 1600 the world was not dominated by Europe. Some of the largest, richest '
                    'and most advanced societies were in <strong>Asia</strong> and <strong>Africa</strong>. '
                    'This topic asks: <em>what were these societies like before European expansion?</em></p>'
                    '<p>The <strong>Ming dynasty</strong> ruled China from <strong>1368 to 1644</strong>. '
                    'The emperor was seen as the "Son of Heaven" with the <em>Mandate of Heaven</em> to rule. '
                    'He governed through a large <strong>civil service</strong> of scholar-officials who '
                    'were chosen by difficult examinations based on the teachings of Confucius.</p>'
                    '<ul>'
                    '<li>The capital moved to <strong>Beijing</strong>, where the Forbidden City was built.</li>'
                    '<li>The <strong>Great Wall</strong> was rebuilt and strengthened against northern invaders.</li>'
                    '<li>China produced fine <strong>porcelain</strong>, silk and tea, which were in demand '
                    'across the world; much of the world\'s silver flowed into China to pay for them.</li>'
                    '<li>Between <strong>1405 and 1433</strong> Admiral <strong>Zheng He</strong> led seven '
                    'voyages with huge "treasure ships" as far as East Africa, to show Ming power and '
                    'collect tribute.</li>'
                    '</ul>'
                    '<p>After 1433 the voyages stopped and later emperors restricted overseas trade, '
                    'turning attention to defending the northern borders. Historians debate whether this '
                    'was a missed opportunity.</p>'
                ),
                'key_terms': [
                    ('Dynasty', 'A series of rulers from the same family.'),
                    ('Civil service', 'Officials who run the government; in Ming China chosen by examination.'),
                    ('Tribute', 'Gifts or payment given to a stronger ruler as a sign of respect or submission.'),
                    ('Mandate of Heaven', 'The Chinese belief that heaven gives an emperor the right to rule.'),
                ],
                'example': {
                    'title': 'Source analysis activity',
                    'html': (
                        '<p><strong>Source:</strong> Zheng He\'s largest treasure ships are described in Chinese '
                        'records as about 120 m long, far larger than the ships Columbus used in 1492 '
                        '(about 20–30 m).</p>'
                        '<ol>'
                        '<li><em>What does the source tell us?</em> Ming China had advanced shipbuilding '
                        'technology and great resources.</li>'
                        '<li><em>Why might the record be questioned?</em> The sizes come from later official '
                        'records and may be exaggerated; historians compare them with archaeological evidence.</li>'
                        '<li><em>Conclusion:</em> Even if the exact size is uncertain, the voyages show that '
                        'China could have explored the world before Europe did.</li>'
                        '</ol>'
                    ),
                },
                'video': {'id': 'sNx_coTfPxA', 'title': 'The Ming Dynasty', 'channel': '4 Minute Histories', 'minutes': 5},
                'worksheet': {
                    'instructions': 'Answer in full sentences. Use your notes on Ming China.',
                    'exercises': [
                        '1. Give the dates of the Ming dynasty.',
                        '2. Explain how officials in the Ming civil service were chosen.',
                        '3. Name THREE products that made China wealthy through trade.',
                        '4. Who was Zheng He and why were his voyages important?',
                        '5. Why did the Ming emperors rebuild the Great Wall?',
                        '6. Suggest ONE reason why China stopped the great voyages after 1433.',
                    ],
                },
                'quiz': [
                    ('mcq', 'Which dynasty ruled China around 1600?',
                     ['Han', 'Qing', 'Ming', 'Tang'], 2),
                    ('mcq', 'How were Ming scholar-officials mainly selected?',
                     ['By inheritance', 'By the army', 'By election', 'By examinations'], 3),
                    ('tf', 'Zheng He\'s fleets reached the coast of East Africa.', True),
                    ('mcq', 'Which city became the Ming capital where the Forbidden City was built?',
                     ['Shanghai', 'Hong Kong', 'Beijing', 'Nanjing only'], 2),
                ],
                'homework': {
                    'title': 'Ming China fact file',
                    'instructions': 'Create a one-page fact file on Ming China using your notes and the video.',
                    'tasks': [
                        'Write the dates and capital city of the Ming dynasty.',
                        'List three achievements of Ming China with one sentence each.',
                        'Write a paragraph (6–8 lines): "Was ending the treasure voyages a mistake?"',
                    ],
                    'marks': 15,
                },
            },
            {
                'title': 'The Songhai Empire of West Africa',
                'minutes': 45,
                'objectives': [
                    'Learners will locate the Songhai Empire and its main cities on a map.',
                    'Learners will explain how trans-Saharan trade made Songhai wealthy.',
                    'Learners will describe the role of Timbuktu as a centre of Islamic learning.',
                    'Learners will explain why Songhai fell in 1591.',
                ],
                'notes': (
                    '<p>The <strong>Songhai Empire</strong> was the largest empire in West African history. '
                    'It grew along the <strong>Niger River</strong> from about <strong>1464</strong>, when '
                    '<strong>Sunni Ali</strong> captured Timbuktu and Djenné. Its capital was '
                    '<strong>Gao</strong>.</p>'
                    '<p><strong>Askia Muhammad</strong> (ruled 1493–1528) organised the empire into provinces '
                    'with governors, created a professional army, standardised weights and measures, and '
                    'supported Islam. He made a famous pilgrimage to Mecca.</p>'
                    '<ul>'
                    '<li><strong>Trade:</strong> Songhai controlled the <em>trans-Saharan trade</em>. Gold from '
                    'the south was exchanged for <strong>salt</strong>, cloth and horses brought across the '
                    'Sahara by camel caravans.</li>'
                    '<li><strong>Learning:</strong> <strong>Timbuktu</strong> was a centre of scholarship with the '
                    'Sankore mosque-university and thousands of manuscripts on law, astronomy, medicine and '
                    'mathematics.</li>'
                    '<li><strong>Decline:</strong> In <strong>1591</strong> a Moroccan army armed with guns '
                    'defeated Songhai at the <strong>Battle of Tondibi</strong>. Civil wars and the shift of '
                    'trade to the Atlantic coast (where Europeans traded) weakened the empire.</li>'
                    '</ul>'
                    '<p>Songhai challenges the old, false idea that Africa had no history or learning before '
                    'Europeans arrived.</p>'
                ),
                'key_terms': [
                    ('Trans-Saharan trade', 'Trade across the Sahara Desert between West Africa and North Africa.'),
                    ('Caravan', 'A group of traders travelling together, often with camels.'),
                    ('Manuscript', 'A book or document written by hand.'),
                    ('Askia', 'The title used by the rulers of the Songhai dynasty founded by Askia Muhammad.'),
                ],
                'example': {
                    'title': 'Class activity: the gold–salt trade',
                    'html': (
                        '<p>Draw a simple flow diagram on the board:</p>'
                        '<p><strong>Gold mines (south)</strong> &raquo; <strong>Timbuktu / Gao markets</strong> '
                        '&raquo; <strong>camel caravans across the Sahara</strong> &raquo; <strong>North Africa</strong></p>'
                        '<p>and in the opposite direction: <strong>salt, cloth, horses, books</strong>.</p>'
                        '<p><em>Discuss:</em> Why could salt be as valuable as gold? (It was essential for '
                        'preserving food and for health in a hot climate, and was scarce in the south.) '
                        'Who benefited most? (The Songhai rulers, who taxed the trade passing through '
                        'their cities.)</p>'
                    ),
                },
                'video': {'id': '5u-3l_AG6TI', 'title': 'grade 10 - Songhai Empire part 1', 'channel': 'the History Crew', 'minutes': 10},
                'worksheet': {
                    'instructions': 'Answer the questions on the Songhai Empire.',
                    'exercises': [
                        '1. Along which river did the Songhai Empire develop?',
                        '2. Name the capital city of Songhai.',
                        '3. Describe TWO reforms introduced by Askia Muhammad.',
                        '4. Explain how the gold-salt trade worked.',
                        '5. Why was Timbuktu important as a centre of learning?',
                        '6. Give TWO reasons for the fall of Songhai in 1591.',
                    ],
                },
                'quiz': [
                    ('mcq', 'What was the capital of the Songhai Empire?', ['Timbuktu', 'Gao', 'Cairo', 'Djenné'], 1),
                    ('mcq', 'Which product did Songhai mainly receive from across the Sahara in exchange for gold?',
                     ['Salt', 'Silk', 'Porcelain', 'Tea'], 0),
                    ('tf', 'Timbuktu was known for its scholars and manuscripts.', True),
                    ('mcq', 'In which battle was Songhai defeated by Morocco in 1591?',
                     ['Tondibi', 'Panipat', 'Isandlwana', 'Lepanto'], 0),
                ],
                'homework': {
                    'title': 'Songhai map and paragraph',
                    'instructions': 'Use an atlas or the internet to help you.',
                    'tasks': [
                        'Draw a sketch map of West Africa showing the Niger River, Gao, Timbuktu and the Sahara.',
                        'Write a paragraph explaining how trade made Songhai rich and powerful.',
                    ],
                    'marks': 10,
                },
            },
            {
                'title': 'Mughal India and the Ottoman Empire; comparing the four societies',
                'minutes': 50,
                'objectives': [
                    'Learners will describe key features of Mughal rule under Akbar.',
                    'Learners will explain how the Ottoman Empire controlled trade between Europe and Asia.',
                    'Learners will compare the four societies using criteria such as power, wealth and learning.',
                ],
                'notes': (
                    '<p><strong>Mughal India:</strong> The Mughal Empire was founded by <strong>Babur</strong> '
                    'after the Battle of Panipat in <strong>1526</strong>. Its greatest ruler, '
                    '<strong>Akbar</strong> (1556–1605), ruled a mostly Hindu population as a Muslim emperor. '
                    'He practised <em>religious tolerance</em>, abolished the tax on non-Muslims and appointed '
                    'Hindus to high office. India was rich from cotton textiles, spices and farming. Later, '
                    '<strong>Shah Jahan</strong> built the <strong>Taj Mahal</strong>.</p>'
                    '<p><strong>The Ottoman Empire:</strong> The Ottoman Turks captured '
                    '<strong>Constantinople in 1453</strong> and renamed it Istanbul. Under '
                    '<strong>Suleiman the Magnificent</strong> (1520–1566) the empire stretched across south-east '
                    'Europe, the Middle East and North Africa, and besieged Vienna in 1529. Because the Ottomans '
                    'controlled the land routes between Europe and Asia, European traders looked for '
                    '<strong>sea routes</strong> to India and China.</p>'
                    '<p><strong>Comparing:</strong> All four societies had strong rulers, organised '
                    'government, large armies, rich trade and centres of learning and art. Their power around '
                    '1600 helps explain <em>why</em> Europeans set out on voyages of exploration.</p>'
                ),
                'key_terms': [
                    ('Religious tolerance', 'Allowing people to follow different religions freely.'),
                    ('Sultan', 'The title of the ruler of the Ottoman Empire.'),
                    ('Empire', 'A group of territories or peoples ruled by one ruler or government.'),
                ],
                'example': {
                    'title': 'Comparison table (class activity)',
                    'html': (
                        '<p>Complete a table with the four societies as columns and these rows:</p>'
                        '<ul>'
                        '<li><strong>Ruler:</strong> Ming emperor | Askia Muhammad | Akbar | Suleiman</li>'
                        '<li><strong>Capital:</strong> Beijing | Gao | Agra / Fatehpur Sikri | Istanbul</li>'
                        '<li><strong>Source of wealth:</strong> porcelain, silk, silver | gold–salt trade | '
                        'textiles, spices | control of trade routes</li>'
                        '<li><strong>Learning / culture:</strong> examinations, Forbidden City | Timbuktu '
                        'manuscripts | Taj Mahal, painting | mosques, law codes</li>'
                        '</ul>'
                        '<p>Then answer: <em>Which society do you think was the most powerful in 1600? Give two '
                        'pieces of evidence.</em></p>'
                    ),
                },
                'video': {'id': 'fMsmCxIEQr4', 'title': 'The rise and fall of the Mughal Empire - Stephanie Honchell Smith', 'channel': 'TED-Ed', 'minutes': 6},
                'worksheet': {
                    'instructions': 'Answer the questions on Mughal India and the Ottoman Empire.',
                    'exercises': [
                        '1. Who founded the Mughal Empire and in which year?',
                        '2. Give TWO examples of Akbar\'s policy of religious tolerance.',
                        '3. Which city did the Ottomans capture in 1453? What was it renamed?',
                        '4. Explain why Ottoman control of trade routes encouraged Europeans to explore by sea.',
                        '5. Name ONE similarity between the Songhai and Ottoman empires.',
                        '6. Write a short paragraph: which of the four societies was most powerful around 1600? Why?',
                    ],
                },
                'quiz': [
                    ('mcq', 'Which Mughal emperor was known for religious tolerance?',
                     ['Babur', 'Aurangzeb', 'Akbar', 'Suleiman'], 2),
                    ('mcq', 'In which year did the Ottomans capture Constantinople?', ['1326', '1453', '1526', '1600'], 1),
                    ('tf', 'The Taj Mahal was built by the Ottoman sultan Suleiman.', False),
                    ('mcq', 'Why did Europeans look for sea routes to Asia?',
                     ['The Ottomans controlled the land routes', 'There were no ships in Asia',
                      'The Mughals banned trade', 'Songhai blocked the Indian Ocean'], 0),
                ],
                'homework': {
                    'title': 'Extended paragraph: the world around 1600',
                    'instructions': 'Write a structured paragraph of about 150 words.',
                    'tasks': [
                        'Explain why it is wrong to think that Europe was the most advanced part of the world in 1600.',
                        'Use at least one fact from each of the four societies studied this week.',
                    ],
                    'marks': 15,
                },
            },
        ],
    },
    (11, 'HIST'): {
        'topic': 'Communism in Russia 1900–1940',
        'caps': 'History Grade 11, Term 1, Topic 1: Communism in Russia 1900–1940 — the Russian '
                'revolutions of 1917, Lenin\'s rule (civil war, War Communism, NEP) and Stalin\'s '
                'Five-Year Plans and collectivisation',
        'summary': 'Learners trace how Tsarist Russia became the world\'s first communist state, '
                   'from the causes of the 1917 revolutions to Lenin\'s policies and Stalin\'s economic '
                   'transformation.',
        'days': [
            {
                'title': 'Tsarist Russia and the revolutions of 1917',
                'minutes': 50,
                'objectives': [
                    'Learners will describe the political, social and economic conditions in Tsarist Russia around 1900.',
                    'Learners will explain the impact of the 1905 revolution and the First World War.',
                    'Learners will distinguish between the February and October revolutions of 1917.',
                ],
                'notes': (
                    '<p>Around 1900 Russia was ruled by <strong>Tsar Nicholas II</strong> as an '
                    '<em>autocracy</em> — he had absolute power and there was no elected parliament. Most '
                    'Russians were poor <strong>peasants</strong>; a small but growing class of factory '
                    '<strong>workers</strong> lived in terrible conditions in cities such as St Petersburg.</p>'
                    '<p>Ideas of <strong>Karl Marx</strong> spread: workers (the proletariat) would overthrow '
                    'the capitalists and create a classless, <strong>communist</strong> society. The '
                    '<strong>Bolsheviks</strong>, led by <strong>Vladimir Lenin</strong>, believed a small '
                    'party of professional revolutionaries should lead this revolution.</p>'
                    '<ul>'
                    '<li><strong>1905:</strong> On <em>Bloody Sunday</em> troops fired on peaceful marchers. '
                    'The Tsar granted a parliament (the Duma) but kept most of his power.</li>'
                    '<li><strong>First World War:</strong> military defeats, food shortages and inflation '
                    'destroyed support for the Tsar.</li>'
                    '<li><strong>February 1917:</strong> strikes and army mutinies forced Nicholas II to '
                    '<strong>abdicate</strong>. A <em>Provisional Government</em> took over but kept '
                    'fighting the war.</li>'
                    '<li><strong>October 1917:</strong> the Bolsheviks, promising <em>"Peace, Land and '
                    'Bread"</em>, seized power in Petrograd.</li>'
                    '</ul>'
                ),
                'key_terms': [
                    ('Autocracy', 'A system in which one ruler has total power.'),
                    ('Proletariat', 'In Marxist theory, the working class who sell their labour.'),
                    ('Bolsheviks', 'The radical Marxist party led by Lenin that seized power in October 1917.'),
                    ('Abdicate', 'To give up the throne.'),
                ],
                'example': {
                    'title': 'Causes table (guided activity)',
                    'html': (
                        '<p>Sort the causes of the February 1917 revolution into categories:</p>'
                        '<ul>'
                        '<li><strong>Long-term:</strong> autocracy, peasant poverty, poor factory conditions, '
                        'spread of Marxist ideas.</li>'
                        '<li><strong>Short-term:</strong> defeats in the First World War, food and fuel '
                        'shortages, the Tsar taking personal command of the army.</li>'
                        '<li><strong>Trigger:</strong> strikes and bread riots in Petrograd; soldiers joining '
                        'the protesters.</li>'
                        '</ul>'
                        '<p><em>Question:</em> Which category was most important? A good answer argues that the '
                        'war turned long-term problems into a crisis the Tsar could not survive.</p>'
                    ),
                },
                'video': {'id': 'U6KR4cLLVzQ', 'title': 'Russian Revolution and Civil War: Crash Course European History #35', 'channel': 'CrashCourse', 'minutes': 14},
                'worksheet': {
                    'instructions': 'Answer in full sentences.',
                    'exercises': [
                        '1. Define "autocracy" and explain how it applied to Russia in 1900.',
                        '2. What happened on Bloody Sunday (January 1905)?',
                        '3. Explain THREE ways the First World War weakened the Tsar.',
                        '4. What was the Provisional Government and why did it become unpopular?',
                        '5. Explain the Bolshevik slogan "Peace, Land and Bread".',
                        '6. Compare the February and October revolutions (who led them and what changed).',
                    ],
                },
                'quiz': [
                    ('mcq', 'Who was the last Tsar of Russia?',
                     ['Alexander II', 'Lenin', 'Peter the Great', 'Nicholas II'], 3),
                    ('mcq', 'Which party seized power in October 1917?', ['Mensheviks', 'Liberals', 'Bolsheviks', 'Monarchists'], 2),
                    ('tf', 'The Provisional Government took Russia out of the First World War immediately.', False),
                    ('mcq', 'What was the parliament created after the 1905 revolution called?',
                     ['The Duma', 'The Soviet', 'The Politburo', 'The Cheka'], 0),
                ],
                'homework': {
                    'title': 'Timeline 1900–1917',
                    'instructions': 'Draw an annotated timeline of the events that led to the October Revolution.',
                    'tasks': [
                        'Include at least six dated events from 1905 to October 1917.',
                        'Add one sentence under each event explaining its importance.',
                    ],
                    'marks': 12,
                },
            },
            {
                'title': 'Lenin in power: civil war, War Communism and the NEP',
                'minutes': 50,
                'objectives': [
                    'Learners will explain how the Bolsheviks consolidated power after 1917.',
                    'Learners will describe the causes and outcome of the Russian Civil War.',
                    'Learners will compare War Communism with the New Economic Policy (NEP).',
                ],
                'notes': (
                    '<p>Lenin moved quickly to keep power. Land was given to the peasants, factories were '
                    'placed under workers\' control, and the secret police (<strong>Cheka</strong>) crushed '
                    'opponents. In <strong>March 1918</strong> the <strong>Treaty of Brest-Litovsk</strong> '
                    'took Russia out of the war, but at the cost of huge areas of land.</p>'
                    '<p>From <strong>1918 to about 1921</strong> a brutal <strong>civil war</strong> was fought '
                    'between the communist <strong>Reds</strong> and the anti-communist <strong>Whites</strong>, '
                    'who were supported by foreign troops. The Red Army, organised by <strong>Leon Trotsky</strong>, '
                    'won because it controlled the central cities and railways and the Whites were divided.</p>'
                    '<p>To feed the army, Lenin introduced <strong>War Communism</strong>: the state took over '
                    'all industry, private trade was banned and grain was seized from peasants. The result was '
                    'famine and unrest, including the <strong>Kronstadt</strong> sailors\' revolt of 1921.</p>'
                    '<p>Lenin then introduced the <strong>New Economic Policy (NEP)</strong> in 1921. Peasants '
                    'could sell surplus grain, small businesses could trade for profit, but the state kept '
                    'the "commanding heights" (banks, heavy industry, foreign trade). Production recovered. '
                    'The USSR was formed in 1922 and Lenin died in <strong>January 1924</strong>.</p>'
                ),
                'key_terms': [
                    ('War Communism', 'Lenin\'s emergency economic policy (1918–1921) of state control and grain seizure.'),
                    ('NEP', 'New Economic Policy (1921): a partial return to private trade and small-scale capitalism.'),
                    ('Cheka', 'The Bolshevik secret police.'),
                    ('USSR', 'Union of Soviet Socialist Republics, formed in 1922.'),
                ],
                'example': {
                    'title': 'Compare and contrast: War Communism vs NEP',
                    'html': (
                        '<ul>'
                        '<li><strong>Grain:</strong> War Communism — seized by the state; NEP — peasants pay a '
                        'tax and sell the surplus.</li>'
                        '<li><strong>Trade:</strong> War Communism — private trade banned; NEP — small traders '
                        '("Nepmen") allowed.</li>'
                        '<li><strong>Industry:</strong> War Communism — all nationalised; NEP — large industry '
                        'state-owned, small firms private.</li>'
                        '<li><strong>Result:</strong> War Communism — famine, revolt; NEP — recovery, but '
                        'many Bolsheviks saw it as a betrayal of communism.</li>'
                        '</ul>'
                        '<p><em>Lenin called the NEP "a step backward in order to take two steps forward".</em> '
                        'Discuss what he meant.</p>'
                    ),
                },
                'video': {'id': '5U5duV94Ocs', 'title': "Lenin's Economic Policy: From War Communism to NEP", 'channel': 'Russel Tarr', 'minutes': 6},
                'worksheet': {
                    'instructions': 'Answer the questions on Lenin\'s rule.',
                    'exercises': [
                        '1. What were the terms and consequences of the Treaty of Brest-Litovsk?',
                        '2. Who fought in the Russian Civil War? Give TWO reasons why the Reds won.',
                        '3. Describe THREE features of War Communism.',
                        '4. Why did the Kronstadt revolt worry Lenin?',
                        '5. Explain how the NEP differed from War Communism.',
                        '6. Was the NEP a success? Give evidence for and against.',
                    ],
                },
                'quiz': [
                    ('mcq', 'Which treaty took Russia out of the First World War?',
                     ['Versailles', 'Brest-Litovsk', 'Locarno', 'Yalta'], 1),
                    ('mcq', 'Who organised the Red Army during the civil war?', ['Stalin', 'Kerensky', 'Trotsky', 'Nicholas II'], 2),
                    ('tf', 'Under the NEP peasants were allowed to sell surplus grain for profit.', True),
                    ('mcq', 'In which year was the NEP introduced?', ['1917', '1919', '1921', '1928'], 2),
                ],
                'homework': {
                    'title': 'Lenin: hero or tyrant?',
                    'instructions': 'Write a balanced paragraph of about 150 words.',
                    'tasks': [
                        'Give two achievements of Lenin and two examples of repression under his rule.',
                        'End with your own supported judgement.',
                    ],
                    'marks': 15,
                },
            },
            {
                'title': 'Stalin\'s Five-Year Plans and collectivisation',
                'minutes': 50,
                'objectives': [
                    'Learners will explain how Stalin rose to power after Lenin\'s death.',
                    'Learners will describe the aims and results of the Five-Year Plans.',
                    'Learners will evaluate the human cost of collectivisation and the purges.',
                ],
                'notes': (
                    '<p>After Lenin died, <strong>Joseph Stalin</strong> used his position as General Secretary '
                    'of the Communist Party to appoint loyal supporters and defeat rivals such as Trotsky. By '
                    '<strong>1928</strong> he was the unchallenged leader. He believed in <em>"socialism in one '
                    'country"</em>: the USSR had to industrialise fast to survive.</p>'
                    '<p><strong>Five-Year Plans</strong> (from 1928): the state planning agency '
                    '<strong>Gosplan</strong> set huge targets for coal, steel, oil and electricity. New industrial '
                    'cities such as Magnitogorsk were built. Output of heavy industry rose dramatically, but '
                    'consumer goods were scarce and workers faced harsh discipline.</p>'
                    '<p><strong>Collectivisation</strong>: private farms were combined into large state-controlled '
                    '<strong>collective farms</strong> (kolkhozes). Wealthier peasants, called '
                    '<strong>kulaks</strong>, were blamed for resistance and deported or killed. Peasants '
                    'slaughtered animals rather than hand them over. The result was a terrible '
                    '<strong>famine in 1932–1933</strong>, especially in Ukraine, in which millions died.</p>'
                    '<p>In the <strong>Great Terror (1936–1938)</strong> Stalin purged the party, army and '
                    'ordinary citizens through show trials, executions and the <strong>Gulag</strong> labour '
                    'camps. By 1940 the USSR was an industrial power — at enormous human cost.</p>'
                ),
                'key_terms': [
                    ('Five-Year Plan', 'A state plan setting production targets for the economy over five years.'),
                    ('Collectivisation', 'Combining private peasant farms into large state-controlled farms.'),
                    ('Kulak', 'A relatively wealthy peasant; targeted as a "class enemy" under Stalin.'),
                    ('Purge', 'The removal of people seen as enemies, through arrest, imprisonment or execution.'),
                ],
                'example': {
                    'title': 'Working with statistics (source activity)',
                    'html': (
                        '<p><strong>Source (approximate Soviet figures):</strong> coal output rose from about '
                        '35 million tonnes (1927) to about 128 million tonnes (1937); steel from about 4 to '
                        '18 million tonnes.</p>'
                        '<ol>'
                        '<li>Calculate the increase in coal: 128 − 35 = 93 million tonnes, roughly '
                        '<strong>3.7 times</strong> the 1927 level.</li>'
                        '<li><em>Reliability:</em> Soviet figures were produced by the state and managers were '
                        'under pressure to report success, so they may be exaggerated.</li>'
                        '<li><em>What the figures do not show:</em> famine, forced labour, poor living '
                        'conditions — so they give only part of the picture.</li>'
                        '</ol>'
                    ),
                },
                'video': {'id': 'ns8yqdUH9ZE', 'title': "What Were Stalin's 5-Year Plans? AP Euro Bit by Bit #41", 'channel': 'AP Euro Bit by Bit with Paul Sargent', 'minutes': 6},
                'worksheet': {
                    'instructions': 'Answer the questions on Stalin\'s USSR.',
                    'exercises': [
                        '1. Explain TWO ways Stalin was able to defeat his rivals after 1924.',
                        '2. What were the main aims of the Five-Year Plans?',
                        '3. Give TWO successes and TWO failures of the Five-Year Plans.',
                        '4. What was collectivisation and why did many peasants resist it?',
                        '5. Who were the kulaks and what happened to them?',
                        '6. "Stalin modernised the USSR, but at too high a price." Do you agree? Explain.',
                    ],
                },
                'quiz': [
                    ('mcq', 'In which year did the first Five-Year Plan begin?', ['1921', '1924', '1928', '1936'], 2),
                    ('mcq', 'What were collective farms called?', ['Kolkhozes', 'Soviets', 'Dumas', 'Gulags'], 0),
                    ('tf', 'The famine of 1932–1933 was linked to collectivisation and grain requisitioning.', True),
                    ('mcq', 'Which state agency drew up the targets of the Five-Year Plans?',
                     ['Cheka', 'NKVD', 'Comintern', 'Gosplan'], 3),
                ],
                'homework': {
                    'title': 'Essay plan: Stalin\'s economic policies',
                    'instructions': 'Plan (do not write in full) an essay on the question below.',
                    'tasks': [
                        'Question: "To what extent were Stalin\'s economic policies a success?"',
                        'Write an introduction with a clear line of argument.',
                        'List three body paragraphs, each with a topic sentence and two pieces of evidence.',
                    ],
                    'marks': 20,
                },
            },
        ],
    },
    (12, 'HIST'): {
        'topic': 'The Cold War: the origins of the Cold War',
        'caps': 'History Grade 12, Term 1, Topic 1: The Cold War — the origins of the Cold War '
                '(Yalta and Potsdam, the Iron Curtain, the Truman Doctrine and Marshall Plan, the '
                'Berlin crisis and the division of Europe)',
        'summary': 'Learners investigate how the wartime alliance between the USA and the USSR broke '
                   'down after 1945 and how Europe was divided into two hostile blocs.',
        'days': [
            {
                'title': 'From allies to rivals: ideology, Yalta and Potsdam',
                'minutes': 50,
                'objectives': [
                    'Learners will define the Cold War and explain the ideological differences between the superpowers.',
                    'Learners will explain the decisions taken at Yalta and Potsdam in 1945.',
                    'Learners will explain why mistrust grew between the USA and the USSR.',
                ],
                'notes': (
                    '<p>The <strong>Cold War</strong> (c. 1945–1991) was a state of tension between the '
                    '<strong>USA</strong> and the <strong>USSR</strong> and their allies. They never fought '
                    'each other directly; instead they competed through propaganda, an arms race, alliances '
                    'and wars fought by others ("proxy wars").</p>'
                    '<p>The two superpowers had opposing <strong>ideologies</strong>:</p>'
                    '<ul>'
                    '<li><strong>USA — capitalism and liberal democracy:</strong> private ownership, free '
                    'markets, multi-party elections, individual freedoms.</li>'
                    '<li><strong>USSR — communism:</strong> state ownership, a planned economy, one-party rule '
                    'by the Communist Party.</li>'
                    '</ul>'
                    '<p>They were allies against Nazi Germany, but at the wartime conferences the cracks showed. '
                    'At <strong>Yalta (February 1945)</strong> Roosevelt, Churchill and Stalin agreed to divide '
                    'Germany into four zones and to hold free elections in liberated Eastern Europe. At '
                    '<strong>Potsdam (July–August 1945)</strong> Truman had replaced Roosevelt; he was more '
                    'suspicious of Stalin, and told him of a powerful new weapon — the atomic bomb. Disputes '
                    'arose over Poland, German reparations and Soviet control of Eastern Europe.</p>'
                    '<p>Stalin wanted a <em>buffer zone</em> of friendly states to protect the USSR from another '
                    'invasion; the West saw this as communist expansion.</p>'
                ),
                'key_terms': [
                    ('Cold War', 'A state of hostility without direct fighting between the superpowers.'),
                    ('Superpower', 'A state with enormous military, economic and political power.'),
                    ('Ideology', 'A set of political, economic and social beliefs.'),
                    ('Buffer zone', 'A neutral or friendly area between rival powers that protects one of them.'),
                ],
                'example': {
                    'title': 'Perspective activity: two views of Eastern Europe',
                    'html': (
                        '<p>Divide the class into two groups.</p>'
                        '<ul>'
                        '<li><strong>Soviet view:</strong> "The USSR lost about 20 million people in the war. '
                        'Germany invaded through Poland twice in 30 years. We need friendly governments on our '
                        'border."</li>'
                        '<li><strong>American view:</strong> "At Yalta Stalin promised free elections. Installing '
                        'communist governments breaks that promise and shows the USSR wants to spread '
                        'communism."</li>'
                        '</ul>'
                        '<p>Each group presents its case; then the class discusses why <em>both</em> sides felt '
                        'threatened — the key to understanding the origins of the Cold War.</p>'
                    ),
                },
                'video': {'id': 'BlFjNf4f0mE', 'title': 'Origins of the Cold War', 'channel': 'Khan Academy', 'minutes': 12},
                'worksheet': {
                    'instructions': 'Answer the questions in full sentences.',
                    'exercises': [
                        '1. Define the term "Cold War".',
                        '2. Compare capitalism and communism under THREE headings: ownership, economy, politics.',
                        '3. List THREE agreements made at the Yalta Conference.',
                        '4. How had the leadership of the USA and Britain changed by the Potsdam Conference?',
                        '5. Explain why Stalin wanted a buffer zone in Eastern Europe.',
                        '6. How did the atomic bomb increase mistrust between the superpowers?',
                    ],
                },
                'quiz': [
                    ('mcq', 'Which leader represented the USA at Potsdam?', ['Roosevelt', 'Truman', 'Eisenhower', 'Kennedy'], 1),
                    ('mcq', 'At Yalta, Germany was to be divided into how many zones?', ['Two', 'Three', 'Four', 'Six'], 2),
                    ('tf', 'The USA and the USSR fought each other directly in a major war during the Cold War.', False),
                    ('mcq', 'Which ideology did the USSR follow?', ['Capitalism', 'Communism', 'Fascism', 'Liberal democracy'], 1),
                ],
                'homework': {
                    'title': 'Yalta vs Potsdam',
                    'instructions': 'Complete a comparison and short explanation.',
                    'tasks': [
                        'Draw a table comparing Yalta and Potsdam: date, leaders, agreements, disagreements.',
                        'Write 6–8 lines explaining why relations were worse at Potsdam than at Yalta.',
                    ],
                    'marks': 12,
                },
            },
            {
                'title': 'The Iron Curtain, the Truman Doctrine and the Marshall Plan',
                'minutes': 50,
                'objectives': [
                    'Learners will explain how the USSR established control over Eastern Europe.',
                    'Learners will explain the meaning of Churchill\'s "Iron Curtain" speech.',
                    'Learners will explain the policy of containment, the Truman Doctrine and the Marshall Plan.',
                    'Learners will describe the Soviet response (Cominform and Comecon).',
                ],
                'notes': (
                    '<p>Between 1945 and 1948 communist governments, backed by the Soviet army, took power in '
                    'Poland, Hungary, Romania, Bulgaria and Czechoslovakia. These became <strong>satellite '
                    'states</strong> of the USSR. In <strong>March 1946</strong>, in Fulton (USA), '
                    '<strong>Winston Churchill</strong> declared that "an <strong>iron curtain</strong> has '
                    'descended across the Continent", dividing a free West from a Soviet-controlled East.</p>'
                    '<p>The USA adopted a policy of <strong>containment</strong> — stopping the spread of '
                    'communism.</p>'
                    '<ul>'
                    '<li><strong>Truman Doctrine (March 1947):</strong> the USA would support "free peoples" '
                    'resisting outside pressure or armed minorities. Aid was given to Greece and Turkey.</li>'
                    '<li><strong>Marshall Plan (1947/8):</strong> about <strong>$13 billion</strong> in economic '
                    'aid to rebuild Western Europe, so that poverty would not make communism attractive. The '
                    'USSR refused it and forbade its satellites to accept it.</li>'
                    '</ul>'
                    '<p>Stalin saw this as "dollar imperialism". He set up <strong>Cominform</strong> (1947) to '
                    'co-ordinate communist parties and <strong>Comecon</strong> (1949) to link the economies of '
                    'the Eastern bloc. Europe was now divided economically as well as politically.</p>'
                ),
                'key_terms': [
                    ('Containment', 'The US policy of preventing the spread of communism.'),
                    ('Satellite state', 'A country formally independent but controlled by a more powerful state.'),
                    ('Iron Curtain', 'Churchill\'s term for the division between Western and Eastern Europe.'),
                    ('Comecon', 'Council for Mutual Economic Assistance (1949), the Soviet bloc\'s economic organisation.'),
                ],
                'example': {
                    'title': 'Source analysis: a cartoon interpretation',
                    'html': (
                        '<p>Show learners a typical Soviet cartoon of the Marshall Plan in which "dollars" are '
                        'used as bait or chains for European countries.</p>'
                        '<ol>'
                        '<li><em>Message:</em> The cartoonist argues that American aid is a trap to control '
                        'Europe.</li>'
                        '<li><em>Context:</em> Produced after the USSR rejected the Marshall Plan in 1947.</li>'
                        '<li><em>Usefulness:</em> Useful for showing the Soviet <strong>perspective</strong>, '
                        'but limited because it is propaganda and one-sided.</li>'
                        '</ol>'
                        '<p>Model the answer structure: <strong>Message + evidence from the source + context + '
                        'limitation</strong>.</p>'
                    ),
                },
                'video': {'id': 'QuIAM5tqP1s', 'title': 'The Truman Doctrine & Marshall Plan | USA Begins Containment', 'channel': 'Mr Hassan History', 'minutes': 8},
                'worksheet': {
                    'instructions': 'Answer the questions on the division of Europe.',
                    'exercises': [
                        '1. Name FOUR countries that became Soviet satellite states by 1948.',
                        '2. Explain what Churchill meant by an "iron curtain".',
                        '3. Define containment.',
                        '4. What did the Truman Doctrine promise? Which countries first received aid?',
                        '5. Explain TWO aims of the Marshall Plan.',
                        '6. Why did Stalin reject the Marshall Plan and what did he set up instead?',
                    ],
                },
                'quiz': [
                    ('mcq', 'Who gave the "Iron Curtain" speech in 1946?', ['Truman', 'Stalin', 'Churchill', 'Marshall'], 2),
                    ('mcq', 'What was the main aim of the US policy of containment?',
                     ['To defeat Germany', 'To unite Europe under the USSR', 'To stop the spread of communism', 'To end the arms race'], 2),
                    ('tf', 'Greece and Turkey were the first countries to receive aid under the Truman Doctrine.', True),
                    ('mcq', 'Which organisation did the USSR create in 1949 to link Eastern bloc economies?',
                     ['NATO', 'Comecon', 'the United Nations', 'the Marshall Plan'], 1),
                ],
                'homework': {
                    'title': 'Paragraph: dollar imperialism?',
                    'instructions': 'Write a paragraph of about 150 words.',
                    'tasks': [
                        'Was the Marshall Plan a generous gift or a political weapon? Use evidence from both perspectives.',
                    ],
                    'marks': 10,
                },
            },
            {
                'title': 'The Berlin crisis 1948–1949 and the division of Germany',
                'minutes': 50,
                'objectives': [
                    'Learners will explain the causes of the Berlin Blockade.',
                    'Learners will describe the Berlin Airlift and its outcome.',
                    'Learners will explain how the crisis led to NATO and two German states.',
                ],
                'notes': (
                    '<p>After 1945 Germany and its capital <strong>Berlin</strong> were divided into four '
                    'zones. Berlin lay deep inside the Soviet zone. The Western powers wanted to rebuild '
                    'Germany\'s economy; in <strong>June 1948</strong> they introduced a new currency, the '
                    '<strong>Deutschmark</strong>, in their zones and West Berlin.</p>'
                    '<p>Stalin feared a strong, Western-controlled Germany. He responded with the '
                    '<strong>Berlin Blockade (June 1948 – May 1949)</strong>, cutting all road, rail and canal '
                    'routes into West Berlin to force the West out.</p>'
                    '<p>The West refused to leave or to use force. Instead it organised the '
                    '<strong>Berlin Airlift</strong>: British and American aircraft flew food, coal and '
                    'medicine into the city — at its peak a plane landed every few minutes. In <strong>May '
                    '1949</strong> Stalin lifted the blockade; the West had won a propaganda victory.</p>'
                    '<ul>'
                    '<li><strong>April 1949:</strong> <strong>NATO</strong> was formed — a military alliance '
                    'of the USA, Canada and Western European states.</li>'
                    '<li><strong>1949:</strong> Germany split into the <strong>Federal Republic (West '
                    'Germany)</strong> and the <strong>German Democratic Republic (East Germany)</strong>.</li>'
                    '<li><strong>August 1949:</strong> the USSR tested its first atomic bomb — the arms race '
                    'had begun.</li>'
                    '</ul>'
                ),
                'key_terms': [
                    ('Blockade', 'Cutting off access to a place to force it to surrender.'),
                    ('Airlift', 'Transporting supplies by aircraft when land routes are blocked.'),
                    ('NATO', 'North Atlantic Treaty Organisation (1949), a Western military alliance.'),
                    ('Arms race', 'Competition between states to build more and better weapons.'),
                ],
                'example': {
                    'title': 'Writing an essay introduction (model)',
                    'html': (
                        '<p><strong>Question:</strong> "The Berlin crisis of 1948–1949 turned the Cold War into a '
                        'permanent division of Europe." Do you agree?</p>'
                        '<p><strong>Model introduction:</strong> <em>This essay agrees with the statement. Although '
                        'tension had grown since Yalta and Potsdam, the Berlin Blockade was the first major '
                        'confrontation of the Cold War. The Airlift showed the West\'s determination, and the '
                        'crisis led directly to NATO and to the creation of two German states in 1949, fixing the '
                        'division of Europe for forty years.</em></p>'
                        '<p>Point out: a clear stance, a line of argument, and a preview of the evidence.</p>'
                    ),
                },
                'video': {'id': 'w_ohOJFJtJI', 'title': 'The Berlin Crisis 1948 | Berlin Blockade and Berlin Airlift', 'channel': 'Mr Hassan History', 'minutes': 8},
                'worksheet': {
                    'instructions': 'Answer the questions on the Berlin crisis.',
                    'exercises': [
                        '1. Why was Berlin a problem for the Western powers after 1945?',
                        '2. Explain how the introduction of the Deutschmark led to the blockade.',
                        '3. Describe the Berlin Airlift.',
                        '4. Why did Stalin lift the blockade in May 1949?',
                        '5. Name the two German states formed in 1949.',
                        '6. Explain how the Berlin crisis contributed to the formation of NATO.',
                    ],
                },
                'quiz': [
                    ('mcq', 'When did the Berlin Blockade begin?', ['June 1945', 'June 1948', 'May 1949', 'August 1961'], 1),
                    ('mcq', 'How did the West supply West Berlin during the blockade?',
                     ['By an airlift', 'By sea', 'By tunnels', 'By rail through Poland'], 0),
                    ('tf', 'NATO was formed in 1949.', True),
                    ('mcq', 'What happened in August 1949 that intensified the arms race?',
                     ['The USSR tested an atomic bomb', 'The Berlin Wall was built', 'Stalin died', 'The Korean War ended'], 0),
                ],
                'homework': {
                    'title': 'Essay paragraph: the Berlin crisis',
                    'instructions': 'Use the model introduction from class.',
                    'tasks': [
                        'Write one body paragraph (PEEL: Point, Evidence, Explanation, Link) on the consequences of the Berlin crisis.',
                        'Write a two-sentence conclusion for the essay.',
                    ],
                    'marks': 15,
                },
            },
        ],
    },
    # ---------------------------------------------------------------- GEOGRAPHY
    (10, 'GEOG'): {
        'topic': 'The atmosphere: composition, structure and heating',
        'caps': 'Geography Grade 10, Term 1, Climatology — The atmosphere: composition of the '
                'atmosphere, structure (layers) of the atmosphere, heating of the atmosphere and the '
                'greenhouse effect',
        'summary': 'Learners study what the atmosphere is made of, its four main layers and how it is '
                   'heated, including the natural greenhouse effect.',
        'days': [
            {
                'title': 'Composition of the atmosphere',
                'minutes': 45,
                'objectives': [
                    'Learners will define the atmosphere and explain its importance for life.',
                    'Learners will name the main gases in the atmosphere and their approximate percentages.',
                    'Learners will explain the role of variable gases, water vapour and aerosols.',
                ],
                'notes': (
                    '<p>The <strong>atmosphere</strong> is the layer of gases surrounding the Earth, held in '
                    'place by gravity. It provides oxygen, protects us from harmful ultraviolet (UV) radiation '
                    'and meteors, keeps the Earth warm, and is where weather happens.</p>'
                    '<p><strong>Permanent gases</strong> (by volume of dry air):</p>'
                    '<ul>'
                    '<li><strong>Nitrogen (N2)</strong> — about <strong>78%</strong>; needed for plant '
                    'growth through the nitrogen cycle.</li>'
                    '<li><strong>Oxygen (O2)</strong> — about <strong>21%</strong>; needed for respiration and '
                    'burning.</li>'
                    '<li><strong>Argon</strong> — about <strong>0.93%</strong>; an inert gas.</li>'
                    '</ul>'
                    '<p><strong>Variable gases</strong> make up a tiny fraction but are very important:</p>'
                    '<ul>'
                    '<li><strong>Carbon dioxide (CO2)</strong> — about 0.04%; absorbs heat (a greenhouse gas) '
                    'and is used in photosynthesis. Burning fossil fuels increases it.</li>'
                    '<li><strong>Water vapour</strong> — 0 to about 4%; forms clouds and rain and absorbs heat.</li>'
                    '<li><strong>Ozone (O3)</strong> — concentrated in the stratosphere, where it absorbs UV '
                    'radiation.</li>'
                    '</ul>'
                    '<p>The air also contains <strong>aerosols</strong> — tiny solid particles such as dust, '
                    'smoke, salt and pollen. They act as <em>condensation nuclei</em> on which water vapour '
                    'condenses to form clouds.</p>'
                ),
                'key_terms': [
                    ('Atmosphere', 'The envelope of gases surrounding the Earth.'),
                    ('Greenhouse gas', 'A gas that absorbs and re-emits heat (long-wave radiation), e.g. CO2, water vapour.'),
                    ('Aerosols', 'Tiny solid or liquid particles suspended in the air.'),
                    ('Condensation nuclei', 'Particles on which water vapour condenses to form droplets.'),
                ],
                'example': {
                    'title': 'Skills activity: drawing a pie chart of the atmosphere',
                    'html': (
                        '<p>A pie chart has 360°. Convert each percentage into degrees:</p>'
                        '<ul>'
                        '<li>Nitrogen: 78% × 360° = <strong>280.8° (about 281°)</strong></li>'
                        '<li>Oxygen: 21% × 360° = <strong>75.6° (about 76°)</strong></li>'
                        '<li>Argon and other gases: 1% × 360° = <strong>3.6° (about 4°)</strong></li>'
                        '</ul>'
                        '<p>Check: 281 + 76 + 4 = 361° — rounding causes the extra degree, so reduce the largest '
                        'slice to 280°. Draw the chart with a protractor, add a key and a title.</p>'
                        '<p><em>Discuss:</em> CO2 is too small to see on the chart. Why is it still so important?</p>'
                    ),
                },
                'video': {'id': 'mWhkRMLEeDc', 'title': 'Composition of Earth’s Atmosphere Explained | Gases, Formulas & Percentages | #Atmosphere', 'channel': 'EduCore', 'minutes': 5},
                'worksheet': {
                    'instructions': 'Answer all the questions on the composition of the atmosphere.',
                    'exercises': [
                        '1. Define the term atmosphere.',
                        '2. Name the two most abundant gases and give their percentages.',
                        '3. Explain the difference between permanent and variable gases.',
                        '4. Give TWO reasons why carbon dioxide is important.',
                        '5. What is the function of ozone in the atmosphere?',
                        '6. Explain how aerosols help clouds to form.',
                        '7. Give TWO human activities that change the composition of the atmosphere.',
                    ],
                },
                'quiz': [
                    ('mcq', 'Which gas makes up about 78% of the atmosphere?',
                     ['Oxygen', 'Carbon dioxide', 'Nitrogen', 'Argon'], 2),
                    ('mcq', 'Approximately what percentage of the atmosphere is oxygen?', ['0.04%', '1%', '21%', '78%'], 2),
                    ('tf', 'Aerosols act as condensation nuclei for cloud formation.', True),
                    ('mcq', 'Which gas absorbs harmful ultraviolet radiation in the stratosphere?', ['Argon', 'Nitrogen', 'Ozone', 'Methane'], 2),
                ],
                'homework': {
                    'title': 'Pie chart of the atmosphere',
                    'instructions': 'Use a protractor and ruler.',
                    'tasks': [
                        'Draw an accurate pie chart of the composition of the atmosphere with a key and title.',
                        'Write a short paragraph on why carbon dioxide levels are rising.',
                    ],
                    'marks': 10,
                },
            },
            {
                'title': 'The structure (layers) of the atmosphere',
                'minutes': 45,
                'objectives': [
                    'Learners will name and describe the layers of the atmosphere in order.',
                    'Learners will explain how temperature changes with height in each layer.',
                    'Learners will calculate temperature change using the normal lapse rate.',
                ],
                'notes': (
                    '<p>The atmosphere is divided into layers according to how <strong>temperature changes '
                    'with height</strong>. The boundaries between layers are called <em>pauses</em>.</p>'
                    '<ol>'
                    '<li><strong>Troposphere</strong> (surface to about 12 km; about 8 km at the poles and 16–18 km '
                    'at the equator). Contains most of the air and water vapour; all <em>weather</em> occurs '
                    'here. Temperature <strong>decreases</strong> by about <strong>6.5 °C per 1 000 m</strong> '
                    '(the normal lapse rate). Ends at the <strong>tropopause</strong>.</li>'
                    '<li><strong>Stratosphere</strong> (about 12–50 km). Temperature <strong>increases</strong> '
                    'with height because the <strong>ozone layer</strong> absorbs UV radiation. Calm, stable air '
                    '— jet aircraft fly in the lower stratosphere. Ends at the stratopause.</li>'
                    '<li><strong>Mesosphere</strong> (about 50–80 km). Temperature <strong>decreases</strong> to '
                    'about −90 °C, the coldest part of the atmosphere. Meteors burn up here.</li>'
                    '<li><strong>Thermosphere</strong> (above about 80 km). Temperature <strong>increases</strong> '
                    'sharply as gases absorb solar radiation. Contains the <em>ionosphere</em>, which reflects '
                    'radio waves; auroras occur here.</li>'
                    '</ol>'
                    '<p>Beyond the thermosphere, the thin <em>exosphere</em> merges with space.</p>'
                ),
                'key_terms': [
                    ('Troposphere', 'The lowest layer of the atmosphere, where weather occurs.'),
                    ('Normal lapse rate', 'The average decrease in temperature with height in the troposphere: about 6.5 °C per 1 000 m.'),
                    ('Tropopause', 'The boundary between the troposphere and the stratosphere.'),
                    ('Ozone layer', 'A concentration of ozone in the stratosphere that absorbs UV radiation.'),
                ],
                'example': {
                    'title': 'Worked example: the normal lapse rate',
                    'html': (
                        '<p>The temperature at Durban (sea level) is 24 °C. What is the expected temperature at '
                        'the top of a mountain 3 000 m high?</p>'
                        '<ol>'
                        '<li>Lapse rate = 6.5 °C per 1 000 m.</li>'
                        '<li>Height difference = 3 000 m = 3 × 1 000 m.</li>'
                        '<li>Temperature drop = 3 × 6.5 = <strong>19.5 °C</strong>.</li>'
                        '<li>Temperature at the top = 24 − 19.5 = <strong>4.5 °C</strong>.</li>'
                        '</ol>'
                        '<p><em>Why?</em> Air is heated from the ground below, and air at height is less dense '
                        'and holds less heat.</p>'
                    ),
                },
                'video': {'id': 'KXf39bQH6iE', 'title': 'Layers of the Atmosphere (Animation)', 'channel': 'KINETIC SCHOOL', 'minutes': 5},
                'worksheet': {
                    'instructions': 'Answer the questions. Show all calculations.',
                    'exercises': [
                        '1. Name the four main layers of the atmosphere from the ground upwards.',
                        '2. In which layer does all weather occur? Why?',
                        '3. Explain why temperature increases with height in the stratosphere.',
                        '4. Which layer is the coldest? Give its approximate minimum temperature.',
                        '5. The temperature at sea level is 20 °C. Calculate the temperature at 2 000 m.',
                        '6. Why is the troposphere thicker at the equator than at the poles?',
                        '7. Draw a labelled graph showing how temperature changes with height through all four layers.',
                    ],
                },
                'quiz': [
                    ('mcq', 'In which layer does weather occur?', ['Stratosphere', 'Mesosphere', 'Troposphere', 'Thermosphere'], 2),
                    ('mcq', 'What is the normal lapse rate?', ['1 °C per 1 000 m', '6.5 °C per 1 000 m', '10 °C per 100 m', '65 °C per 1 000 m'], 1),
                    ('tf', 'Temperature increases with height in the stratosphere because of the ozone layer.', True),
                    ('mcq', 'In which layer do most meteors burn up?', ['Troposphere', 'Stratosphere', 'Mesosphere', 'Exosphere'], 2),
                ],
                'homework': {
                    'title': 'Lapse rate calculations',
                    'instructions': 'Show all working.',
                    'tasks': [
                        'Sea level temperature is 28 °C. Calculate the temperature at 1 000 m, 2 500 m and 4 000 m.',
                        'Draw and label a cross-section diagram of the four layers with their approximate heights.',
                    ],
                    'marks': 12,
                },
            },
            {
                'title': 'Heating of the atmosphere and the greenhouse effect',
                'minutes': 45,
                'objectives': [
                    'Learners will explain how the atmosphere is heated by radiation, conduction and convection.',
                    'Learners will explain the natural greenhouse effect.',
                    'Learners will distinguish between the natural and enhanced greenhouse effect.',
                ],
                'notes': (
                    '<p>The Sun sends energy to Earth as <strong>short-wave radiation</strong> '
                    '(<em>insolation</em> — incoming solar radiation). The atmosphere is not heated much by '
                    'this directly. Instead, the <strong>Earth\'s surface absorbs</strong> the energy, warms '
                    'up and then heats the air above it.</p>'
                    '<ul>'
                    '<li><strong>Radiation:</strong> the warm ground gives off <strong>long-wave '
                    '(terrestrial) radiation</strong>, which greenhouse gases absorb.</li>'
                    '<li><strong>Conduction:</strong> air in direct contact with the warm ground is heated.</li>'
                    '<li><strong>Convection:</strong> heated air expands, becomes less dense and rises, '
                    'carrying heat upwards; cooler air sinks to replace it.</li>'
                    '<li><strong>Advection:</strong> heat is moved horizontally by wind.</li>'
                    '</ul>'
                    '<p><strong>The greenhouse effect:</strong> greenhouse gases (water vapour, CO2, methane) '
                    'let short-wave radiation through but <strong>absorb and re-radiate long-wave radiation</strong>, '
                    'trapping heat. Without this <em>natural</em> greenhouse effect the Earth\'s average temperature '
                    'would be about −18 °C instead of about 15 °C.</p>'
                    '<p>The <strong>enhanced greenhouse effect</strong> happens when human activities (burning '
                    'coal, oil and gas; deforestation; livestock farming) add extra greenhouse gases, trapping '
                    'more heat and causing <strong>global warming</strong>.</p>'
                ),
                'key_terms': [
                    ('Insolation', 'Incoming solar radiation (short-wave).'),
                    ('Terrestrial radiation', 'Long-wave heat radiation given off by the Earth\'s surface.'),
                    ('Convection', 'The transfer of heat by the rising of warm air and sinking of cool air.'),
                    ('Enhanced greenhouse effect', 'Extra warming caused by greenhouse gases released by humans.'),
                ],
                'example': {
                    'title': 'Class demonstration: why the ground heats the air',
                    'html': (
                        '<p>On a sunny day, compare the temperature of a tar road and the air 1.5 m above it '
                        '(or use a picture of a mirage above a hot road).</p>'
                        '<ol>'
                        '<li>The tar absorbs short-wave insolation and becomes very hot.</li>'
                        '<li>Air touching the tar is heated by <strong>conduction</strong>.</li>'
                        '<li>The warm air rises by <strong>convection</strong> — the shimmering above the road.</li>'
                        '<li>The road also gives off <strong>long-wave radiation</strong>, which we feel as heat.</li>'
                        '</ol>'
                        '<p><em>Conclusion:</em> the atmosphere is heated mainly <strong>from below</strong>, '
                        'which is why temperature decreases with height in the troposphere.</p>'
                    ),
                },
                'video': {'id': 'SN5-DnOHQmE', 'title': 'What Is the Greenhouse Effect?', 'channel': 'NASA Space Place', 'minutes': 3},
                'worksheet': {
                    'instructions': 'Answer all the questions.',
                    'exercises': [
                        '1. Define insolation.',
                        '2. Explain the difference between short-wave and long-wave radiation.',
                        '3. Describe how air is heated by conduction and convection.',
                        '4. Explain why the atmosphere is heated mainly from below.',
                        '5. Draw a labelled diagram of the natural greenhouse effect.',
                        '6. List THREE human activities that cause the enhanced greenhouse effect.',
                        '7. Give TWO possible effects of global warming on South Africa.',
                    ],
                },
                'quiz': [
                    ('mcq', 'What type of radiation does the Earth\'s surface give off?',
                     ['Short-wave radiation', 'Long-wave radiation', 'Ultraviolet radiation', 'X-rays'], 1),
                    ('tf', 'Without the natural greenhouse effect the Earth would be much colder.', True),
                    ('mcq', 'Which process moves heat horizontally through the atmosphere?', ['Conduction', 'Convection', 'Advection', 'Reflection'], 2),
                    ('mcq', 'Which activity contributes most to the enhanced greenhouse effect?',
                     ['Burning fossil fuels', 'Planting trees', 'Using solar panels', 'Recycling paper'], 0),
                ],
                'homework': {
                    'title': 'Greenhouse effect explained',
                    'instructions': 'Explain the greenhouse effect to a Grade 7 learner.',
                    'tasks': [
                        'Draw and label a diagram of the natural greenhouse effect.',
                        'Write 8–10 lines explaining how human activities enhance it and what the consequences are.',
                    ],
                    'marks': 10,
                },
            },
        ],
    },
    (11, 'GEOG'): {
        'topic': 'The Earth\'s energy balance and global air circulation',
        'caps': 'Geography Grade 11, Term 1, Climatology — The Earth\'s energy balance (heat budget), '
                'unequal heating between latitudes, and the global air circulation (pressure belts, '
                'planetary winds, three-cell model)',
        'summary': 'Learners explain how the Earth balances incoming and outgoing energy, why the tropics '
                   'have a surplus and the poles a deficit, and how the global circulation of air redistributes heat.',
        'days': [
            {
                'title': 'The Earth\'s energy balance (heat budget)',
                'minutes': 50,
                'objectives': [
                    'Learners will describe what happens to incoming solar radiation.',
                    'Learners will explain the concept of albedo.',
                    'Learners will explain why low latitudes have an energy surplus and high latitudes a deficit.',
                ],
                'notes': (
                    '<p>The Earth\'s <strong>energy balance</strong> (or heat budget) is the balance between '
                    'incoming solar radiation and outgoing radiation. Over a year, the Earth as a whole neither '
                    'heats up nor cools down (apart from recent global warming), so input equals output.</p>'
                    '<p>Of 100 units of insolation reaching the top of the atmosphere, roughly:</p>'
                    '<ul>'
                    '<li><strong>30 units are reflected</strong> back to space by clouds, the atmosphere and '
                    'bright surfaces. This is the Earth\'s <strong>albedo</strong> (about 30%).</li>'
                    '<li><strong>about 20 units are absorbed</strong> by the atmosphere (gases, clouds, dust).</li>'
                    '<li><strong>about 50 units are absorbed</strong> by the Earth\'s surface.</li>'
                    '</ul>'
                    '<p>The surface then returns this energy to the atmosphere by long-wave radiation, '
                    'conduction, convection and <em>latent heat</em> (energy released when water vapour '
                    'condenses).</p>'
                    '<p><strong>Unequal heating:</strong> between about 38°N and 38°S there is an energy '
                    '<strong>surplus</strong>; towards the poles there is a <strong>deficit</strong>. Reasons: '
                    'the Sun\'s rays strike the tropics at a higher <em>angle of incidence</em> (energy '
                    'concentrated on a smaller area), pass through less atmosphere, and polar ice has a high '
                    'albedo. The tropics do not keep getting hotter because heat is transferred polewards by '
                    '<strong>winds (about 80%)</strong> and <strong>ocean currents (about 20%)</strong>.</p>'
                ),
                'key_terms': [
                    ('Energy balance', 'The balance between incoming solar and outgoing terrestrial radiation.'),
                    ('Albedo', 'The percentage of incoming radiation that a surface reflects.'),
                    ('Angle of incidence', 'The angle at which the Sun\'s rays strike the Earth\'s surface.'),
                    ('Latent heat', 'Heat absorbed or released when water changes state, e.g. during condensation.'),
                ],
                'example': {
                    'title': 'Worked example: albedo and the angle of incidence',
                    'html': (
                        '<p><strong>(a) Albedo:</strong> A surface receives 800 W/m² and reflects 680 W/m². '
                        'Albedo = 680 ÷ 800 × 100 = <strong>85%</strong> — typical of fresh snow. A dark forest '
                        'reflecting 80 W/m² of 800 W/m² has an albedo of only <strong>10%</strong>.</p>'
                        '<p><strong>(b) Angle of incidence:</strong> Shine a torch straight down onto paper '
                        '(like the overhead Sun at the equator) and then at a low angle (like the Sun near the '
                        'poles). The same light covers a <em>larger area</em> at a low angle, so each square '
                        'metre receives <strong>less energy</strong>.</p>'
                        '<p><em>Conclusion:</em> high-latitude regions are colder because of low sun angles '
                        'and high albedo.</p>'
                    ),
                },
                'video': {'id': 'zE3x2wjslt0', 'title': "Real World: Earth's Energy Balance - Energy In and Energy Out", 'channel': 'NASA eClips - ARCHIVE', 'minutes': 5},
                'worksheet': {
                    'instructions': 'Answer the questions. Show calculations.',
                    'exercises': [
                        '1. Define the Earth\'s energy balance.',
                        '2. What percentage of insolation is reflected by the Earth (its albedo)?',
                        '3. Calculate the albedo of a surface that receives 500 W/m2 and reflects 150 W/m2.',
                        '4. Explain THREE reasons why the tropics receive more energy than the poles.',
                        '5. Name the two ways heat is transferred from the tropics to the poles.',
                        '6. Explain why melting polar ice may speed up global warming.',
                    ],
                },
                'quiz': [
                    ('mcq', "What is the Earth's average albedo?",
                     ['About 30%', 'About 5%', 'About 70%', 'About 95%'], 0),
                    ('mcq', 'Which surface has the highest albedo?', ['Dark forest', 'Ocean', 'Fresh snow', 'Tar road'], 2),
                    ('tf', 'Low latitudes have an energy deficit and high latitudes have an energy surplus.', False),
                    ('mcq', 'Which carries most of the heat from the tropics towards the poles?', ['Ocean currents', 'Winds', 'Rivers', 'Volcanoes'], 1),
                ],
                'homework': {
                    'title': 'Energy balance diagram',
                    'instructions': 'Use your notes.',
                    'tasks': [
                        'Draw a labelled flow diagram showing what happens to 100 units of insolation.',
                        'Explain in 6–8 lines why there is an energy surplus at the equator and a deficit at the poles.',
                    ],
                    'marks': 12,
                },
            },
            {
                'title': 'Global air circulation: pressure belts and the three-cell model',
                'minutes': 50,
                'objectives': [
                    'Learners will name and locate the global pressure belts.',
                    'Learners will explain how the Hadley, Ferrel and Polar cells form.',
                    'Learners will link rising and sinking air to rainfall and deserts.',
                ],
                'notes': (
                    '<p>Unequal heating creates differences in air pressure. <strong>Warm air rises</strong>, '
                    'creating <strong>low pressure</strong> at the surface; <strong>cool air sinks</strong>, '
                    'creating <strong>high pressure</strong>. Air moves from high to low pressure as '
                    '<strong>wind</strong>.</p>'
                    '<p>The global <strong>pressure belts</strong> are:</p>'
                    '<ul>'
                    '<li><strong>Equatorial low</strong> (0°) — the <em>Inter-Tropical Convergence Zone (ITCZ)</em>; '
                    'intense heating, rising air, heavy convectional rain.</li>'
                    '<li><strong>Subtropical highs</strong> (about 30° N and S) — sinking, dry air; most of the '
                    'world\'s hot deserts (e.g. the Namib and Kalahari) are found here.</li>'
                    '<li><strong>Subpolar lows</strong> (about 60° N and S) — warm and cold air meet and rise; '
                    'cloudy and wet.</li>'
                    '<li><strong>Polar highs</strong> (90°) — cold, dense, sinking air.</li>'
                    '</ul>'
                    '<p>These belts are linked by three circulation <strong>cells</strong> in each hemisphere:</p>'
                    '<ol>'
                    '<li><strong>Hadley cell</strong> (0–30°): air rises at the equator, flows polewards aloft, '
                    'sinks at 30° and returns to the equator at the surface.</li>'
                    '<li><strong>Ferrel cell</strong> (30–60°): surface air flows polewards from 30° and rises at '
                    '60°; it is driven by the other two cells.</li>'
                    '<li><strong>Polar cell</strong> (60–90°): cold air sinks at the pole and flows towards 60°.</li>'
                    '</ol>'
                ),
                'key_terms': [
                    ('ITCZ', 'Inter-Tropical Convergence Zone: the equatorial low-pressure belt where the trade winds meet.'),
                    ('Pressure gradient', 'The difference in pressure between two places, which drives wind.'),
                    ('Hadley cell', 'The tropical circulation cell between the equator and about 30°.'),
                    ('Subtropical high', 'A belt of high pressure and sinking air at about 30° latitude.'),
                ],
                'example': {
                    'title': 'Guided diagram: the three-cell model',
                    'html': (
                        '<p>Draw a large circle (the Earth). Mark the latitudes 0°, 30°, 60° and 90° in both '
                        'hemispheres.</p>'
                        '<ol>'
                        '<li>At 0° write <strong>L</strong> and draw an arrow <em>up</em> (rising air, rain).</li>'
                        '<li>At 30° write <strong>H</strong> and draw an arrow <em>down</em> (sinking air, deserts).</li>'
                        '<li>At 60° write <strong>L</strong> and an <em>up</em> arrow; at 90° write <strong>H</strong> '
                        'and a <em>down</em> arrow.</li>'
                        '<li>Join the arrows into loops to form the Hadley, Ferrel and Polar cells.</li>'
                        '</ol>'
                        '<p><em>Apply:</em> Explain why the Namib Desert lies at about 23–25° S while the Congo '
                        'rainforest lies near 0°.</p>'
                    ),
                },
                'video': {'id': 'xqM83_og1Fc', 'title': 'What is global circulation? | Part Two | The three cells', 'channel': 'Met Office - Learn About Weather', 'minutes': 4},
                'worksheet': {
                    'instructions': 'Answer the questions on global air circulation.',
                    'exercises': [
                        '1. Explain why rising air leads to low pressure at the surface.',
                        '2. Name the four pressure belts in the Southern Hemisphere and their latitudes.',
                        '3. Describe the circulation of air in the Hadley cell.',
                        '4. Why is the Ferrel cell described as an "indirect" cell?',
                        '5. Explain why many deserts are found at about 30° latitude.',
                        '6. Draw and label the three-cell model for one hemisphere.',
                    ],
                },
                'quiz': [
                    ('mcq', 'What type of pressure is found at about 30° N and S?', ['Low pressure', 'High pressure', 'No pressure', 'Variable pressure only'], 1),
                    ('mcq', 'Which cell lies between the equator and about 30°?', ['Polar cell', 'Ferrel cell', 'Hadley cell', 'Walker cell'], 2),
                    ('tf', 'The ITCZ is associated with rising air and heavy rainfall.', True),
                    ('mcq', 'Air moves from ...',
                     ['low pressure to high pressure', 'land to sea only', 'the poles upward only', 'high pressure to low pressure'], 3),
                ],
                'homework': {
                    'title': 'Three-cell model',
                    'instructions': 'Use an atlas map of world climates.',
                    'tasks': [
                        'Draw the three-cell model for both hemispheres.',
                        'Name one desert and one rainforest and explain their locations using the pressure belts.',
                    ],
                    'marks': 12,
                },
            },
            {
                'title': 'Planetary winds, the Coriolis force and seasonal shifts',
                'minutes': 50,
                'objectives': [
                    'Learners will explain the Coriolis force and its effect in each hemisphere.',
                    'Learners will name and locate the planetary winds.',
                    'Learners will explain how the seasonal shift of the pressure belts affects South Africa\'s climate.',
                ],
                'notes': (
                    '<p>Because the Earth rotates, moving air is deflected. This is the <strong>Coriolis '
                    'force</strong>: winds are deflected to the <strong>left in the Southern Hemisphere</strong> '
                    'and to the <strong>right in the Northern Hemisphere</strong>. It is zero at the equator and '
                    'strongest at the poles.</p>'
                    '<p>The <strong>planetary winds</strong> blow from the high-pressure belts to the low-pressure '
                    'belts and are deflected by the Coriolis force:</p>'
                    '<ul>'
                    '<li><strong>Trade winds</strong> (30° to 0°): in the Southern Hemisphere they become the '
                    '<strong>South-East Trades</strong>; in the Northern Hemisphere the North-East Trades.</li>'
                    '<li><strong>Westerlies</strong> (30° to 60°): in the Southern Hemisphere they blow from the '
                    'north-west/west; they are strong over the oceans ("Roaring Forties").</li>'
                    '<li><strong>Polar easterlies</strong> (90° to 60°).</li>'
                    '</ul>'
                    '<p><strong>Seasonal shift:</strong> the pressure belts move with the overhead Sun. In the '
                    'southern <em>winter</em> (June–August) they shift <strong>north</strong>, so the westerlies '
                    'and their cold fronts reach the south-western Cape — giving the Western Cape its '
                    '<strong>winter rainfall</strong>. In <em>summer</em> they shift south; the interior receives '
                    'convectional thunderstorms and the south-western Cape is dry.</p>'
                ),
                'key_terms': [
                    ('Coriolis force', 'The apparent deflection of moving air caused by the Earth\'s rotation.'),
                    ('Trade winds', 'Steady winds blowing from the subtropical highs towards the equator.'),
                    ('Westerlies', 'Winds blowing from the subtropical highs towards the subpolar lows.'),
                    ('Seasonal shift', 'The movement of the pressure belts north and south with the overhead Sun.'),
                ],
                'example': {
                    'title': 'Worked reasoning: predicting wind direction',
                    'html': (
                        '<p><strong>Question:</strong> Air flows from the subtropical high (30° S) towards the '
                        'equatorial low (0°). What wind results?</p>'
                        '<ol>'
                        '<li>Without rotation, the air would flow due <strong>north</strong> (from 30° S towards 0°).</li>'
                        '<li>In the Southern Hemisphere, Coriolis deflects it to the <strong>left</strong>, i.e. towards '
                        'the north-west.</li>'
                        '<li>So the wind blows <em>from</em> the south-east: the <strong>South-East Trade wind</strong>. '
                        '(Winds are named after the direction they come from.)</li>'
                        '</ol>'
                        '<p><em>Try:</em> use the same steps for air flowing from 30° S to 60° S. (Answer: '
                        'deflected left, i.e. towards the south-east, giving the <strong>westerlies / north-westerlies</strong>.)</p>'
                    ),
                },
                'video': {'id': 'oZ6exQoU_CM', 'title': 'Global Pressures and Wind Belts', 'channel': 'Earth Explained', 'minutes': 6},
                'worksheet': {
                    'instructions': 'Answer all the questions.',
                    'exercises': [
                        '1. Define the Coriolis force.',
                        '2. In which direction are winds deflected in the Southern Hemisphere?',
                        '3. Name the planetary winds of the Southern Hemisphere and the pressure belts they blow between.',
                        '4. Explain why the trade winds in the Southern Hemisphere blow from the south-east.',
                        '5. Explain why Cape Town receives most of its rain in winter.',
                        '6. Why does the Highveld receive most of its rain in summer?',
                    ],
                },
                'quiz': [
                    ('mcq', 'In the Southern Hemisphere the Coriolis force deflects winds to the ...',
                     ['right', 'left', 'north only', 'equator only'], 1),
                    ('mcq', 'Which winds blow between 30° S and the equator?',
                     ['South-East Trades', 'Westerlies', 'Polar easterlies', 'Berg winds'], 0),
                    ('tf', 'In winter the pressure belts shift northwards, bringing cold fronts to the Western Cape.', True),
                    ('mcq', 'Where is the Coriolis force zero?', ['At the poles', 'At 30°', 'At 60°', 'At the equator'], 3),
                ],
                'homework': {
                    'title': 'Global winds map',
                    'instructions': 'Use a blank world map or draw a circle diagram.',
                    'tasks': [
                        'Mark the pressure belts and draw arrows for the planetary winds in both hemispheres.',
                        'Write a paragraph explaining how the seasonal shift of the pressure belts affects rainfall in South Africa.',
                    ],
                    'marks': 15,
                },
            },
        ],
    },
    (12, 'GEOG'): {
        'topic': 'Climate and weather: mid-latitude cyclones',
        'caps': 'Geography Grade 12, Term 1, Climate and weather — Mid-latitude cyclones: area of '
                'formation, stages of development, associated weather (cold and warm fronts) and '
                'identification on synoptic weather maps',
        'summary': 'Learners explain how mid-latitude cyclones form along the polar front, how they '
                   'develop and occlude, and how they affect South African weather, including reading them on '
                   'synoptic maps.',
        'days': [
            {
                'title': 'Formation of mid-latitude cyclones',
                'minutes': 50,
                'objectives': [
                    'Learners will define a mid-latitude cyclone and state where it forms.',
                    'Learners will explain the role of the polar front in cyclone formation.',
                    'Learners will describe the pressure and wind circulation of a mid-latitude cyclone in the Southern Hemisphere.',
                ],
                'notes': (
                    '<p>A <strong>mid-latitude cyclone</strong> (also called a frontal depression or temperate '
                    'cyclone) is a large <strong>low-pressure</strong> system that forms between about '
                    '<strong>30° and 60° S</strong>. It brings most of the winter rain to the south-western Cape.</p>'
                    '<p><strong>Formation:</strong></p>'
                    '<ul>'
                    '<li>Along the <strong>polar front</strong> (about 60° S), cold, dense '
                    '<strong>polar air</strong> moving from the south-east meets warm, moist '
                    '<strong>tropical air</strong> carried by the westerlies from the north-west.</li>'
                    '<li>The two air masses do not mix easily. Differences in speed and direction cause a '
                    '<strong>wave</strong> (kink) to form in the front.</li>'
                    '<li>The warm air rises over the cold air, causing <strong>pressure to drop</strong> at the '
                    'tip of the wave — a low-pressure centre develops.</li>'
                    '</ul>'
                    '<p>In the <strong>Southern Hemisphere</strong>, air flows into the low and circulates '
                    '<strong>clockwise</strong> (because Coriolis deflects air to the left). The system moves '
                    '<strong>from west to east</strong>, steered by the westerlies, and is strongest in winter '
                    'when the pressure belts shift north, allowing cyclones to brush the South African coast.</p>'
                ),
                'key_terms': [
                    ('Mid-latitude cyclone', 'A low-pressure system with fronts that forms between 30° and 60° latitude.'),
                    ('Polar front', 'The boundary where cold polar air meets warm tropical air, at about 60° latitude.'),
                    ('Air mass', 'A large body of air with similar temperature and humidity throughout.'),
                    ('Cyclogenesis', 'The process by which a cyclone forms and develops.'),
                ],
                'example': {
                    'title': 'Guided sketch: initial stage of a mid-latitude cyclone',
                    'html': (
                        '<ol>'
                        '<li>Draw a horizontal line across the page — the <strong>polar front</strong>.</li>'
                        '<li>Above it (south) label <strong>cold polar air</strong> with an arrow from the south-east; '
                        'below it (north) label <strong>warm tropical air</strong> with an arrow from the north-west.</li>'
                        '<li>Draw a small northward bulge in the line — the <strong>wave</strong>.</li>'
                        '<li>Mark <strong>L</strong> at the tip of the wave and draw clockwise arrows around it.</li>'
                        '</ol>'
                        '<p><em>Note:</em> In the Southern Hemisphere the warm air is to the <strong>north</strong>, '
                        'so the wave bulges northwards on a map.</p>'
                    ),
                },
                'video': {'id': 'QDPVsK-9k8E', 'title': 'Mid-latitude Cyclones | Formation | Grade 12 Geography | Climatology', 'channel': 'Study Guy', 'minutes': 10},
                'worksheet': {
                    'instructions': 'Answer the questions on the formation of mid-latitude cyclones.',
                    'exercises': [
                        '1. Define a mid-latitude cyclone.',
                        '2. Between which latitudes do mid-latitude cyclones form?',
                        '3. Name the two air masses that meet at the polar front and describe their characteristics.',
                        '4. Explain how a low-pressure centre develops along the polar front.',
                        '5. In which direction do winds circulate around a low in the Southern Hemisphere? Why?',
                        '6. Why do mid-latitude cyclones influence South Africa mainly in winter?',
                    ],
                },
                'quiz': [
                    ('mcq', 'Where do mid-latitude cyclones form?', ['Over the equator', 'Between 5° and 25°', 'Between 30° and 60°', 'Over the poles'], 2),
                    ('mcq', 'In the Southern Hemisphere, air around a low-pressure system circulates ...',
                     ['clockwise', 'anticlockwise', 'directly outward', 'not at all'], 0),
                    ('tf', 'Mid-latitude cyclones move from east to west across the south of South Africa.', False),
                    ('mcq', 'Along which front do mid-latitude cyclones develop?',
                     ['The ITCZ', 'The coastal front', 'The polar front', 'The Moisture front'], 2),
                ],
                'homework': {
                    'title': 'Formation explained',
                    'instructions': 'Write and draw.',
                    'tasks': [
                        'Draw a labelled sketch of the initial stage of a mid-latitude cyclone in the Southern Hemisphere.',
                        'Write a paragraph (8–10 lines) explaining how mid-latitude cyclones form.',
                    ],
                    'marks': 12,
                },
            },
            {
                'title': 'Stages of development: mature stage, occlusion and degeneration',
                'minutes': 50,
                'objectives': [
                    'Learners will describe the stages in the life cycle of a mid-latitude cyclone.',
                    'Learners will identify the cold front, warm front and warm sector.',
                    'Learners will explain how an occlusion forms.',
                ],
                'notes': (
                    '<p>A mid-latitude cyclone develops through several stages over about 3 to 7 days:</p>'
                    '<ol>'
                    '<li><strong>Initial stage:</strong> a wave forms on the polar front and pressure drops.</li>'
                    '<li><strong>Mature (developing) stage:</strong> the low deepens and two fronts form. The '
                    '<strong>cold front</strong> (where cold air pushes under warm air) lies to the '
                    '<strong>west</strong>, and the <strong>warm front</strong> (where warm air rises over cold air) '
                    'lies to the <strong>east</strong>. Between them is the <strong>warm sector</strong>. The '
                    'cyclone has a clear <em>V-shape</em> or wave shape with closed isobars around the low.</li>'
                    '<li><strong>Occluded stage:</strong> the cold front moves faster than the warm front and '
                    '<strong>catches up</strong> with it. The warm air of the warm sector is lifted completely off '
                    'the ground — this is an <strong>occlusion</strong>. Heavy rain and strong winds may occur.</li>'
                    '<li><strong>Degeneration (dissipating) stage:</strong> with no more warm air to lift, the '
                    'system loses energy, pressure rises and the cyclone dies out.</li>'
                    '</ol>'
                    '<p>Often several cyclones follow each other in a "family", which explains why the Western '
                    'Cape can have a series of cold fronts in a week of winter.</p>'
                ),
                'key_terms': [
                    ('Cold front', 'The boundary where advancing cold air undercuts and lifts warm air.'),
                    ('Warm front', 'The boundary where advancing warm air rises gently over cold air.'),
                    ('Warm sector', 'The wedge of warm air between the warm and cold fronts.'),
                    ('Occlusion', 'When the cold front overtakes the warm front and lifts the warm air off the ground.'),
                ],
                'example': {
                    'title': 'Sequence activity: the life cycle in four sketches',
                    'html': (
                        '<p>Draw four boxes in a row and sketch each stage (Southern Hemisphere view):</p>'
                        '<ul>'
                        '<li><strong>Box 1 — Initial:</strong> straight front with a small wave and an L.</li>'
                        '<li><strong>Box 2 — Mature:</strong> cold front (blue line with triangles) to the west, warm '
                        'front (red line with semicircles) to the east, warm sector between them.</li>'
                        '<li><strong>Box 3 — Occluded:</strong> the fronts join near the low to form an occluded '
                        'front (purple line with alternating triangles and semicircles).</li>'
                        '<li><strong>Box 4 — Degeneration:</strong> weak low, few isobars, no warm sector.</li>'
                        '</ul>'
                        '<p>Under each box write one sentence describing what is happening to the warm air.</p>'
                    ),
                },
                'video': {'id': '_4kRXSDlO58', 'title': 'Mid-latitude cyclone - Grade 12 Geography', 'channel': 'Edu-ca-te', 'minutes': 10},
                'worksheet': {
                    'instructions': 'Answer the questions on the stages of development.',
                    'exercises': [
                        '1. List the four stages of a mid-latitude cyclone in the correct order.',
                        '2. Distinguish between a cold front and a warm front.',
                        '3. What is the warm sector?',
                        '4. Explain why the cold front eventually catches up with the warm front.',
                        '5. Explain what happens during occlusion.',
                        '6. Why does the cyclone degenerate after occlusion?',
                        '7. Draw the symbols used for a cold front, warm front and occluded front.',
                    ],
                },
                'quiz': [
                    ('mcq', 'In the Southern Hemisphere, where does the cold front lie in relation to the warm front?',
                     ['To the east', 'To the north', 'Directly on top', 'To the west'], 3),
                    ('mcq', 'What happens during occlusion?',
                     ['The warm front overtakes the cold front', 'The cold front overtakes the warm front',
                      'A new polar front forms', 'The cyclone moves westwards'], 1),
                    ('tf', 'The warm sector lies between the warm front and the cold front.', True),
                    ('mcq', 'Which symbol represents a cold front on a synoptic map?',
                     ['A line with triangles', 'A line with semicircles', 'A dotted line', 'A circle with an H'], 0),
                ],
                'homework': {
                    'title': 'Life cycle diagram',
                    'instructions': 'Present the life cycle as an annotated diagram.',
                    'tasks': [
                        'Draw the four stages of a mid-latitude cyclone with labels and front symbols.',
                        'Annotate each stage with two characteristics.',
                    ],
                    'marks': 15,
                },
            },
            {
                'title': 'Weather associated with fronts and reading synoptic maps',
                'minutes': 50,
                'objectives': [
                    'Learners will describe the weather before, during and after the passage of a cold front.',
                    'Learners will describe the weather associated with a warm front.',
                    'Learners will identify a mid-latitude cyclone and its fronts on a synoptic weather map.',
                ],
                'notes': (
                    '<p>As a mid-latitude cyclone passes Cape Town, the weather changes in a clear pattern.</p>'
                    '<p><strong>Warm front</strong> (gentle slope): warm air rises slowly over cold air. High '
                    '<em>cirrus</em> clouds appear first, followed by thickening <em>altostratus</em> and '
                    '<em>nimbostratus</em>. Steady, light to moderate rain or drizzle; temperatures rise slightly '
                    'afterwards.</p>'
                    '<p><strong>Cold front</strong> (steep slope): cold air pushes warm air up rapidly.</p>'
                    '<ul>'
                    '<li><strong>Before:</strong> warm, humid; pressure falling; winds from the '
                    '<strong>north-west</strong>; cloud building up.</li>'
                    '<li><strong>During:</strong> towering <strong>cumulonimbus</strong> clouds; heavy rain, '
                    'thunder, possibly hail; strong, gusty winds.</li>'
                    '<li><strong>After:</strong> temperature drops sharply; pressure rises; winds swing '
                    '(back) to the <strong>south-west</strong>; skies clear; snow may fall on high mountains.</li>'
                    '</ul>'
                    '<p><strong>On a synoptic map</strong>, a mid-latitude cyclone appears south of the country '
                    'as a low (L or a low value such as 984 hPa) with <strong>closed isobars</strong>, and fronts '
                    'extending northwards towards the coast. Isobars close together mean strong winds. Wind '
                    'arrows on station models show the north-westerly winds ahead of the front and '
                    'south-westerly winds behind it.</p>'
                ),
                'key_terms': [
                    ('Synoptic weather map', 'A map showing weather conditions over a large area at a particular time.'),
                    ('Isobar', 'A line joining places of equal atmospheric pressure.'),
                    ('Cumulonimbus', 'A tall, dense thunderstorm cloud associated with cold fronts.'),
                    ('Station model', 'A symbol showing the weather (temperature, wind, cloud, rain) at one weather station.'),
                ],
                'example': {
                    'title': 'Worked example: interpreting a winter synoptic map',
                    'html': (
                        '<p><strong>Situation:</strong> A low of 988 hPa lies south-west of Cape Town. A cold front '
                        'stretches from the low to just west of Cape Town. Cape Town\'s station model shows '
                        '17 °C, a north-westerly wind of 20 knots and overcast skies.</p>'
                        '<ol>'
                        '<li><em>Stage:</em> Two fronts are visible with a warm sector — the <strong>mature stage</strong>.</li>'
                        '<li><em>Current weather in Cape Town:</em> it is <strong>ahead</strong> of the cold front — '
                        'overcast, mild, north-westerly winds, falling pressure.</li>'
                        '<li><em>Forecast for the next 24 hours:</em> as the front passes — heavy rain and '
                        'thunderstorms; afterwards temperature drops (e.g. to about 11 °C), wind swings to the '
                        'south-west, pressure rises and skies clear.</li>'
                        '</ol>'
                    ),
                },
                'video': {'id': 'cQiZAoocqOw', 'title': 'Grade 10 - 12 Geography: Reading and Interpreting Synoptic Weather Maps', 'channel': 'Geography with Wassie', 'minutes': 15},
                'worksheet': {
                    'instructions': 'Answer the questions. Refer to a winter synoptic map from a newspaper or the SA Weather Service if available.',
                    'exercises': [
                        '1. Describe the clouds and rainfall associated with a warm front.',
                        '2. Describe the weather in Cape Town BEFORE a cold front arrives.',
                        '3. Describe the weather DURING the passage of a cold front.',
                        '4. Explain why temperatures drop after a cold front has passed.',
                        '5. How does wind direction change as a cold front passes Cape Town?',
                        '6. How would you recognise a mid-latitude cyclone on a synoptic map?',
                        '7. What do closely spaced isobars indicate?',
                    ],
                },
                'quiz': [
                    ('mcq', 'Which cloud type is typical of a cold front?',
                     ['Cirrus', 'Stratus only', 'Cumulonimbus', 'No clouds'], 2),
                    ('mcq', 'After a cold front passes Cape Town, the wind usually blows from the ...',
                     ['north-west', 'south-west', 'north-east', 'east'], 1),
                    ('tf', 'Air pressure rises after the passage of a cold front.', True),
                    ('mcq', 'What do closely spaced isobars indicate?',
                     ['Calm conditions', 'Drought', 'High temperatures', 'Strong winds'], 3),
                    ('tf', 'A warm front usually brings short, violent thunderstorms.', False),
                ],
                'homework': {
                    'title': 'Weather forecast from a synoptic map',
                    'instructions': 'Find a recent winter synoptic map (newspaper, SAWS website or textbook).',
                    'tasks': [
                        'Identify and label the mid-latitude cyclone, the cold front and the low-pressure centre.',
                        'Write a 24-hour weather forecast for Cape Town based on the map.',
                        'Explain two possible negative impacts of a strong cold front on people in the Western Cape.',
                    ],
                    'marks': 15,
                },
            },
        ],
    },
    # --------------------------------------------------------------- ACCOUNTING
    (10, 'ACC'): {
        'topic': 'Accounting concepts, GAAP principles and the accounting equation',
        'caps': 'Accounting Grade 10, Term 1 — Financial accounting: accounting concepts (assets, '
                'liabilities, owner\'s equity, income, expenses), GAAP principles, and the accounting '
                'equation (analysis of transactions) for a sole trader',
        'summary': 'Learners build the vocabulary of Accounting, meet the GAAP principles that guide '
                   'bookkeeping, and use the accounting equation A = OE + L to analyse transactions.',
        'days': [
            {
                'title': 'Accounting concepts and GAAP principles',
                'minutes': 50,
                'objectives': [
                    'Learners will define Accounting and the main accounting concepts.',
                    'Learners will classify items as assets, liabilities, owner\'s equity, income or expenses.',
                    'Learners will explain selected GAAP principles with examples.',
                ],
                'notes': (
                    '<p><strong>Accounting</strong> is the process of <em>recording, summarising, analysing '
                    'and interpreting</em> financial information so that owners, managers, banks and SARS can make '
                    'decisions. In Grade 10 we start with a <strong>sole trader</strong> — a business owned by one '
                    'person.</p>'
                    '<p><strong>Key concepts:</strong></p>'
                    '<ul>'
                    '<li><strong>Assets</strong> — resources owned by the business that will bring future '
                    'benefits, e.g. vehicles, equipment, trading stock, debtors, bank.</li>'
                    '<li><strong>Liabilities</strong> — debts the business owes to outsiders, e.g. a loan, '
                    'creditors.</li>'
                    '<li><strong>Owner\'s equity</strong> — the owner\'s interest in the business: capital '
                    'contributed plus profit, minus drawings.</li>'
                    '<li><strong>Income</strong> increases owner\'s equity (e.g. sales, rent income); '
                    '<strong>expenses</strong> decrease it (e.g. wages, water and electricity).</li>'
                    '<li><strong>Drawings</strong> — cash or goods taken by the owner for personal use.</li>'
                    '</ul>'
                    '<p><strong>GAAP</strong> (Generally Accepted Accounting Practice) are the rules that make '
                    'financial statements reliable and comparable:</p>'
                    '<ul>'
                    '<li><strong>Business entity rule:</strong> the business and the owner are separate.</li>'
                    '<li><strong>Historical cost:</strong> assets are recorded at the price paid.</li>'
                    '<li><strong>Prudence:</strong> be cautious — do not overstate assets or income.</li>'
                    '<li><strong>Matching:</strong> expenses are matched with the income of the same period.</li>'
                    '<li><strong>Materiality:</strong> important amounts must be shown separately.</li>'
                    '<li><strong>Going concern:</strong> we assume the business will continue to operate.</li>'
                    '</ul>'
                ),
                'key_terms': [
                    ('Asset', 'Something of value owned by the business that will bring future benefits.'),
                    ('Liability', 'A debt owed by the business to an outside party.'),
                    ('Owner\'s equity', 'The owner\'s claim on the business (capital + profit − drawings).'),
                    ('GAAP', 'Generally Accepted Accounting Practice: the principles that guide financial reporting.'),
                ],
                'example': {
                    'title': 'Worked example: classifying items and applying GAAP',
                    'html': (
                        '<p><strong>Classify:</strong></p>'
                        '<ul>'
                        '<li>Delivery vehicle — <strong>asset</strong></li>'
                        '<li>Loan from ABC Bank — <strong>liability</strong></li>'
                        '<li>Capital contributed by the owner — <strong>owner\'s equity</strong></li>'
                        '<li>Sales of goods — <strong>income</strong></li>'
                        '<li>Wages paid — <strong>expense</strong></li>'
                        '</ul>'
                        '<p><strong>GAAP:</strong> The owner, T. Mokoena, pays her home electricity account of '
                        'R1 200 from the business bank account. Under the <strong>business entity rule</strong> '
                        'this is <em>not</em> a business expense; it is recorded as <strong>drawings</strong>.</p>'
                        '<p>Equipment bought for R18 000 is now worth R25 000 on the market. Under the '
                        '<strong>historical cost</strong> principle it stays in the books at <strong>R18 000</strong>.</p>'
                    ),
                },
                'video': {'id': 'z0kv-a-FGfw', 'title': 'Accounting Concepts & GAAP Principles Explained! | Grade 10 Accounting', 'channel': 'Mr Q the Tutor', 'minutes': 10},
                'worksheet': {
                    'instructions': 'Classify each item as an Asset (A), Liability (L), Owner\'s equity (OE), Income (I) or Expense (E), then answer the GAAP questions.',
                    'exercises': [
                        '1. Trading stock;  2. Rent income;  3. Mortgage loan;  4. Capital;  5. Telephone account paid',
                        '6. Equipment;  7. Creditors;  8. Debtors;  9. Salaries paid;  10. Interest received',
                        '11. Define owner\'s equity and explain how profit and drawings affect it.',
                        '12. The owner takes R500 from the cash register for personal use. Name and explain the GAAP principle involved.',
                        '13. A building bought for R800 000 is now valued at R1 100 000. At what amount is it recorded? Name the principle.',
                        '14. Explain the matching principle in your own words.',
                    ],
                },
                'quiz': [
                    ('mcq', 'Which of the following is an asset?', ['Loan from bank', 'Creditors', 'Equipment', 'Wages'], 2),
                    ('mcq', 'Which GAAP principle states that the business and the owner are separate?',
                     ['Business entity rule', 'Prudence', 'Matching', 'Materiality'], 0),
                    ('tf', 'Expenses decrease owner\'s equity.', True),
                    ('mcq', 'Under the historical cost principle, assets are recorded at ...',
                     ['their current market value', 'the price paid for them', 'their insurance value', 'any value the owner chooses'], 1),
                ],
                'homework': {
                    'title': 'Concepts and GAAP',
                    'instructions': 'Complete in your Accounting exercise book.',
                    'tasks': [
                        'List five assets and three liabilities you might find in a spaza shop.',
                        'Explain the prudence and going concern principles, each with your own example.',
                    ],
                    'marks': 10,
                },
            },
            {
                'title': 'The accounting equation: A = OE + L',
                'minutes': 50,
                'objectives': [
                    'Learners will state the accounting equation and explain why it always balances.',
                    'Learners will calculate a missing value in the accounting equation.',
                    'Learners will explain the effect of income, expenses and drawings on owner\'s equity.',
                ],
                'notes': (
                    '<p>Everything a business owns (its <strong>assets</strong>) is financed either by the '
                    'owner (<strong>owner\'s equity</strong>) or by outsiders (<strong>liabilities</strong>). '
                    'This gives the <strong>accounting equation</strong>:</p>'
                    '<p><strong>Assets = Owner\'s equity + Liabilities</strong> (A = OE + L)</p>'
                    '<p>It can be rearranged: <strong>OE = A − L</strong> and <strong>L = A − OE</strong>.</p>'
                    '<p>The equation <em>always balances</em> because every transaction has a '
                    '<strong>double effect</strong> (the <em>double-entry</em> principle). For example, if the '
                    'business buys equipment for cash, one asset (equipment) increases and another asset (bank) '
                    'decreases by the same amount.</p>'
                    '<p><strong>How owner\'s equity changes:</strong></p>'
                    '<ul>'
                    '<li><strong>Capital contribution</strong> — increases OE.</li>'
                    '<li><strong>Income</strong> (e.g. sales, services rendered, rent income) — increases OE.</li>'
                    '<li><strong>Expenses</strong> (e.g. wages, advertising, stationery) — decrease OE.</li>'
                    '<li><strong>Drawings</strong> by the owner — decrease OE.</li>'
                    '</ul>'
                    '<p><strong>Net profit = Income − Expenses</strong>. Closing owner\'s equity = opening '
                    'capital + capital contributions + net profit − drawings.</p>'
                ),
                'key_terms': [
                    ('Accounting equation', 'A = OE + L: assets equal the sum of owner\'s equity and liabilities.'),
                    ('Double entry', 'Every transaction affects at least two items so that the equation balances.'),
                    ('Net profit', 'Total income minus total expenses for a period.'),
                    ('Drawings', 'Cash, goods or services taken by the owner for personal use.'),
                ],
                'example': {
                    'title': 'Worked example: finding the missing value',
                    'html': (
                        '<p><strong>Thandi\'s Traders</strong> has the following on 31 January:</p>'
                        '<ul>'
                        '<li>Equipment R25 000; Vehicle R60 000; Trading stock R15 000; Bank R10 000</li>'
                        '<li>Loan from FNB R40 000</li>'
                        '</ul>'
                        '<ol>'
                        '<li>Total assets = 25 000 + 60 000 + 15 000 + 10 000 = <strong>R110 000</strong></li>'
                        '<li>Liabilities = <strong>R40 000</strong></li>'
                        '<li>OE = A − L = 110 000 − 40 000 = <strong>R70 000</strong></li>'
                        '<li>Check: OE + L = 70 000 + 40 000 = 110 000 = A. The equation balances.</li>'
                        '</ol>'
                        '<p><strong>Owner\'s equity calculation:</strong> Opening capital R60 000 + net profit '
                        'R14 000 − drawings R4 000 = <strong>R70 000</strong>.</p>'
                    ),
                },
                'video': {'id': 'twLzWucjceE', 'title': 'ACCOUNTING EQUATION: Explained in (Almost) 2 Minutes!', 'channel': 'Accounting Stuff', 'minutes': 3},
                'worksheet': {
                    'instructions': 'Calculate the missing amounts. Show all workings.',
                    'exercises': [
                        '1. Assets R85 000; Liabilities R30 000; Owner\'s equity = ?',
                        '2. Owner\'s equity R120 000; Liabilities R45 000; Assets = ?',
                        '3. Assets R200 000; Owner\'s equity R150 000; Liabilities = ?',
                        '4. Opening capital R50 000; net profit R18 000; drawings R6 000. Calculate closing owner\'s equity.',
                        '5. Income R42 000; expenses R29 500. Calculate net profit.',
                        '6. Explain why the accounting equation must always balance.',
                    ],
                },
                'quiz': [
                    ('mcq', 'Which is the correct accounting equation?',
                     ['A = OE − L', 'L = A + OE', 'OE = A + L', 'A = OE + L'], 3),
                    ('mcq', 'Assets are R90 000 and liabilities are R35 000. What is owner\'s equity?',
                     ['R125 000', 'R55 000', 'R35 000', 'R45 000'], 1),
                    ('tf', 'Drawings increase owner\'s equity.', False),
                    ('mcq', 'Income R30 000 and expenses R22 000 give a net profit of ...', ['R52 000', 'R8 000', 'R22 000', 'R30 000'], 1),
                ],
                'homework': {
                    'title': 'Accounting equation calculations',
                    'instructions': 'Show workings for every calculation.',
                    'tasks': [
                        'Assets R340 000, liabilities R95 000: calculate owner\'s equity.',
                        'Opening capital R75 000, additional capital R10 000, net profit R21 000, drawings R8 500: calculate closing owner\'s equity.',
                        'Explain the double-entry principle using the purchase of a computer for cash as an example.',
                    ],
                    'marks': 12,
                },
            },
            {
                'title': 'Analysing transactions using the accounting equation',
                'minutes': 55,
                'objectives': [
                    'Learners will identify the two accounts affected by a transaction.',
                    'Learners will analyse the effect of transactions on assets, owner\'s equity and liabilities.',
                    'Learners will check that the accounting equation balances after each transaction.',
                ],
                'notes': (
                    '<p>To analyse a transaction, answer these questions:</p>'
                    '<ol>'
                    '<li>Which <strong>two accounts</strong> are affected?</li>'
                    '<li>Is each account an asset, owner\'s equity (or income/expense/drawings) or liability?</li>'
                    '<li>Does each one <strong>increase (+)</strong> or <strong>decrease (−)</strong>, and by how much?</li>'
                    '<li>Does the equation still balance (change in A = change in OE + change in L)?</li>'
                    '</ol>'
                    '<p><strong>Common patterns:</strong></p>'
                    '<ul>'
                    '<li>Owner contributes cash: A + / OE +.</li>'
                    '<li>Buy an asset for cash: A + and A − (no change in total).</li>'
                    '<li>Buy trading stock on credit: A + / L +.</li>'
                    '<li>Receive income: A + / OE +.</li>'
                    '<li>Pay an expense: A − / OE −.</li>'
                    '<li>Owner takes cash for personal use (drawings): A − / OE −.</li>'
                    '<li>Pay a creditor: A − / L −.</li>'
                    '</ul>'
                    '<p>This is the foundation for recording entries in the journals and ledger later in the term.</p>'
                ),
                'key_terms': [
                    ('Transaction', 'A business event that changes the financial position and must be recorded.'),
                    ('Credit purchase', 'Buying goods now and paying for them later (creates a creditor).'),
                    ('Creditor', 'A person or business to whom the business owes money.'),
                ],
                'example': {
                    'title': 'Worked example: Sizwe Stores (January)',
                    'html': (
                        '<ol>'
                        '<li><strong>Owner deposited R50 000 as capital.</strong><br>'
                        'Bank (A) +50 000 | Capital (OE) +50 000 | L 0</li>'
                        '<li><strong>Bought equipment by EFT, R8 000.</strong><br>'
                        'Equipment (A) +8 000, Bank (A) −8 000 | OE 0 | L 0</li>'
                        '<li><strong>Bought trading stock on credit from Lulu Suppliers, R6 000.</strong><br>'
                        'Trading stock (A) +6 000 | OE 0 | Creditors (L) +6 000</li>'
                        '<li><strong>Received rent income, R2 500.</strong><br>'
                        'Bank (A) +2 500 | Rent income (OE) +2 500 | L 0</li>'
                        '<li><strong>Paid wages, R3 000.</strong><br>'
                        'Bank (A) −3 000 | Wages (OE) −3 000 | L 0</li>'
                        '<li><strong>Owner withdrew R1 000 for personal use.</strong><br>'
                        'Bank (A) −1 000 | Drawings (OE) −1 000 | L 0</li>'
                        '</ol>'
                        '<p><strong>Totals:</strong> A = 50 000 + 0 + 6 000 + 2 500 − 3 000 − 1 000 = '
                        '<strong>R54 500</strong>; OE = 50 000 + 2 500 − 3 000 − 1 000 = <strong>R48 500</strong>; '
                        'L = <strong>R6 000</strong>.</p>'
                        '<p>Check: 48 500 + 6 000 = 54 500. <strong>The equation balances.</strong></p>'
                    ),
                },
                'video': {'id': '5MksPBhEhLc', 'title': 'Grade 10 Accounting Equation Term 1 | Accounting Equation Part 1 Analysis of transactions 2026', 'channel': 'Accounting Solution SA', 'minutes': 20},
                'worksheet': {
                    'instructions': 'For each transaction of Bongi\'s Boutique, name the two accounts affected and show the effect (+ / - and amount) on Assets, Owner\'s equity and Liabilities.',
                    'exercises': [
                        '1. The owner, Bongi, deposited R40 000 into the business bank account as capital.',
                        '2. Bought a cash register for R4 500 and paid by EFT.',
                        '3. Bought trading stock on credit from Fashion Wholesalers, R12 000.',
                        '4. Received R1 800 for alterations done for customers (services rendered).',
                        '5. Paid the electricity account, R950.',
                        '6. Paid Fashion Wholesalers R5 000 on account.',
                        '7. Bongi took R700 cash for personal use.',
                        '8. Calculate total A, OE and L after all transactions and prove that the equation balances.',
                    ],
                },
                'quiz': [
                    ('mcq', 'The business buys trading stock on credit. The effect is:',
                     ['A + / OE +', 'A − / L −', 'A + / L +', 'A + / A −'], 2),
                    ('mcq', 'The business pays wages of R2 000. The effect on owner\'s equity is:',
                     ['+R2 000', 'No effect', '−R2 000', '−R4 000'], 2),
                    ('tf', 'Buying equipment with cash does not change total assets.', True),
                    ('mcq', 'Paying a creditor R3 000 has which effect?',
                     ['A − / L −', 'A − / OE −', 'A + / L +', 'OE − / L +'], 0),
                ],
                'homework': {
                    'title': 'Transaction analysis',
                    'instructions': 'Analyse each transaction for Kopano Car Wash using the accounting equation.',
                    'tasks': [
                        'Owner contributed R30 000 cash; bought a pressure washer for R6 500 by EFT; received R2 200 for car washes.',
                        'Bought cleaning materials on credit, R900; paid wages R1 500; owner took R400 for personal use.',
                        'Calculate the totals and prove that A = OE + L.',
                    ],
                    'marks': 20,
                },
            },
        ],
    },
    (11, 'ACC'): {
        'topic': 'Reconciliations: bank reconciliation',
        'caps': 'Accounting Grade 11, Term 1 — Managing resources: reconciliations (bank '
                'reconciliation): comparing the Cash Journals and Bank account with the bank statement, '
                'adjusting the journals and preparing a bank reconciliation statement; internal control',
        'summary': 'Learners explain why the Bank account and the bank statement differ, update the Cash '
                   'Journals for items on the bank statement, and prepare a bank reconciliation statement.',
        'days': [
            {
                'title': 'Why the Bank account and bank statement differ',
                'minutes': 50,
                'objectives': [
                    'Learners will explain the purpose of a bank reconciliation.',
                    'Learners will compare the Bank account in the ledger with the bank statement.',
                    'Learners will classify differences as items the business must record or timing differences.',
                ],
                'notes': (
                    '<p>A business records its receipts in the <strong>Cash Receipts Journal (CRJ)</strong> and '
                    'its payments in the <strong>Cash Payments Journal (CPJ)</strong>; the totals are posted to '
                    'the <strong>Bank account</strong> in the General Ledger. The bank keeps its own record and '
                    'sends a <strong>bank statement</strong>. At month-end the two balances are seldom equal.</p>'
                    '<p><strong>Important:</strong> the bank sees the account from its own side. A '
                    '<em>favourable</em> balance is a <strong>debit</strong> in the business\'s Bank account but a '
                    '<strong>credit</strong> on the bank statement (the bank owes the money to the business).</p>'
                    '<p><strong>Reasons for differences:</strong></p>'
                    '<ol>'
                    '<li><strong>Items on the bank statement not yet in the journals</strong> — the business must '
                    'record these: bank charges, interest on overdraft or interest received, debit orders, '
                    'direct deposits (EFTs) by debtors, dishonoured (returned) payments.</li>'
                    '<li><strong>Items in the journals not yet on the bank statement</strong> (timing '
                    'differences): <em>outstanding deposits</em> made late on the last day, and '
                    '<em>outstanding payments</em> recorded in the CPJ but not yet processed by the bank.</li>'
                    '<li><strong>Errors</strong> by the business or the bank.</li>'
                    '</ol>'
                    '<p>A <strong>bank reconciliation</strong> explains these differences. It is an important '
                    '<strong>internal control</strong> measure: it detects errors and fraud and makes sure '
                    'the Bank balance in the financial statements is correct.</p>'
                ),
                'key_terms': [
                    ('Bank statement', 'The bank\'s record of the business\'s account, sent to the business.'),
                    ('Bank reconciliation', 'A process to explain and correct the differences between the Bank account and the bank statement.'),
                    ('Outstanding deposit', 'An amount recorded in the CRJ that does not yet appear on the bank statement.'),
                    ('Debit order', 'An instruction allowing a creditor to take regular amounts directly from the account.'),
                ],
                'example': {
                    'title': 'Worked example: ticking and classifying',
                    'html': (
                        '<p>Compare the CRJ, CPJ and bank statement of Nala Traders for January and tick matching '
                        'amounts. The unticked items are:</p>'
                        '<ul>'
                        '<li>Bank charges R350 (bank statement only) — <strong>record in CPJ</strong></li>'
                        '<li>Interest on credit balance R120 (bank statement only) — <strong>record in CRJ</strong></li>'
                        '<li>Debit order for insurance R900 (bank statement only) — <strong>record in CPJ</strong></li>'
                        '<li>EFT deposit from a debtor R1 500 (bank statement only) — <strong>record in CRJ</strong></li>'
                        '<li>Deposit R4 000 on 31 January (CRJ only) — <strong>outstanding deposit</strong>, goes on '
                        'the reconciliation statement</li>'
                        '<li>EFT payment R2 230 on 31 January, processed by the bank on 2 February (CPJ only) — '
                        '<strong>outstanding payment</strong>, goes on the reconciliation statement</li>'
                        '</ul>'
                    ),
                },
                'video': {'id': '3n8pIhCkP-E', 'title': 'Grade 11 Accounting Term 1 | Bank Reconciliations Statement Part 1 of 2026 ', 'channel': 'Accounting Solution SA', 'minutes': 20},
                'worksheet': {
                    'instructions': 'Answer the questions. For Q5 state where each item will be recorded: CRJ, CPJ or Bank Reconciliation Statement (BRS).',
                    'exercises': [
                        '1. Explain the purpose of a bank reconciliation.',
                        '2. Why does a favourable balance appear as a credit on the bank statement?',
                        '3. Give THREE examples of items that appear on the bank statement but not in the Cash Journals.',
                        '4. What is an outstanding deposit? Why does it happen?',
                        '5a. Bank charges R280;  5b. Direct deposit by a debtor R2 100;  5c. Deposit of R3 600 made on the last day of the month',
                        '5d. Interest on overdraft R95;  5e. Debit order for a loan repayment R1 750',
                        '6. Explain how a monthly bank reconciliation serves as an internal control measure.',
                    ],
                },
                'quiz': [
                    ('mcq', 'A favourable bank balance appears on the bank statement as a ...',
                     ['debit balance', 'credit balance', 'zero balance', 'liability of the business'], 1),
                    ('mcq', 'Bank charges on the bank statement must be recorded in the ...',
                     ['CRJ', 'CPJ', 'Debtors Journal', 'Creditors Journal'], 1),
                    ('tf', 'An outstanding deposit is recorded in the CRJ but does not yet appear on the bank statement.', True),
                    ('mcq', 'Which item is a timing difference?',
                     ['Bank charges', 'A debit order', 'An outstanding deposit', 'Interest received'], 2),
                ],
                'homework': {
                    'title': 'Classifying reconciliation items',
                    'instructions': 'Classify each item and give a reason.',
                    'tasks': [
                        'Make a table with three columns: Record in CRJ, Record in CPJ, Show on Bank Reconciliation Statement.',
                        'Place these items: service fees R310; EFT from debtor R2 400; deposit on last day R5 200; insurance debit order R1 100; EFT to creditor not yet processed R3 050; interest received R85.',
                    ],
                    'marks': 12,
                },
            },
            {
                'title': 'Updating the Cash Journals and the Bank account',
                'minutes': 55,
                'objectives': [
                    'Learners will enter bank-statement items into the CRJ and CPJ.',
                    'Learners will correct errors made in the Cash Journals.',
                    'Learners will calculate the correct (adjusted) Bank account balance.',
                ],
                'notes': (
                    '<p>Before preparing the reconciliation statement, the business must <strong>update its own '
                    'records</strong> for all items that appear on the bank statement but not in its journals.</p>'
                    '<ul>'
                    '<li><strong>Add to the CRJ</strong> (increase Bank): interest received, direct deposits '
                    'by debtors, any errors where a receipt was under-recorded or a payment was over-recorded.</li>'
                    '<li><strong>Add to the CPJ</strong> (decrease Bank): bank charges, interest on overdraft, '
                    'debit orders, dishonoured (R/D) payments, errors where a payment was under-recorded.</li>'
                    '</ul>'
                    '<p>After the additional totals are posted, the <strong>adjusted Bank account balance</strong> '
                    'is calculated:</p>'
                    '<p><strong>Adjusted balance = Balance before adjustments + extra CRJ total − extra CPJ total</strong></p>'
                    '<p>If the balance is favourable it is a <strong>debit</strong> balance; an overdraft is a '
                    '<strong>credit</strong> balance in the Bank account. Work carefully with signs when the '
                    'account is overdrawn: adding receipts <em>reduces</em> an overdraft.</p>'
                    '<p><strong>Errors:</strong> If the business recorded an EFT payment of R2 860 as R2 680, the '
                    'payment was under-recorded by R180, so <strong>R180 is added to the CPJ</strong>.</p>'
                ),
                'key_terms': [
                    ('Adjusted balance', 'The correct Bank account balance after recording all bank-statement items and errors.'),
                    ('R/D (Refer to drawer)', 'A payment received that the bank could not process, e.g. due to insufficient funds.'),
                    ('Overdraft', 'An unfavourable bank balance: the business owes the bank money.'),
                ],
                'example': {
                    'title': 'Worked example: Nala Traders, 31 January',
                    'html': (
                        '<p>Bank account balance before adjustments: <strong>R12 400 (Dr, favourable)</strong>.</p>'
                        '<p><strong>Additional CRJ entries:</strong></p>'
                        '<ul>'
                        '<li>Interest received R120</li>'
                        '<li>EFT deposit from debtor S. Ndlovu R1 500</li>'
                        '<li>CRJ additional total = <strong>R1 620</strong></li>'
                        '</ul>'
                        '<p><strong>Additional CPJ entries:</strong></p>'
                        '<ul>'
                        '<li>Bank charges R350</li>'
                        '<li>Debit order — insurance R900</li>'
                        '<li>Error: EFT to creditor recorded as R2 680 instead of R2 860 — R180</li>'
                        '<li>CPJ additional total = <strong>R1 430</strong></li>'
                        '</ul>'
                        '<p><strong>Adjusted Bank balance</strong> = 12 400 + 1 620 − 1 430 = '
                        '<strong>R12 590 (Dr, favourable)</strong>.</p>'
                    ),
                },
                'video': {'id': 'GjjvV1dUKrw', 'title': 'Bank Reconciliation Statement Explained | FULL EXAMPLE', 'channel': 'Counttuts', 'minutes': 15},
                'worksheet': {
                    'instructions': 'Calculate the adjusted Bank account balance in each case. Show the extra CRJ and CPJ totals.',
                    'exercises': [
                        '1. Balance R8 600 (Dr). Bank charges R240; direct deposit by debtor R1 900; debit order R650.',
                        '2. Balance R15 300 (Dr). Interest received R75; dishonoured payment from debtor R1 200; service fees R185.',
                        '3. Balance R5 000 (Dr). An EFT payment of R1 450 was recorded in the CPJ as R1 540.',
                        '4. Balance R3 200 (Cr, overdraft). Interest on overdraft R110; EFT deposit by debtor R4 000. Is the new balance favourable or unfavourable?',
                        '5. Explain why the business must record bank charges in its own books.',
                    ],
                },
                'quiz': [
                    ('mcq', 'A direct deposit by a debtor on the bank statement is recorded in the ...',
                     ['CRJ', 'CPJ', 'Bank reconciliation statement only', 'Debtors Journal'], 0),
                    ('mcq', 'Balance R10 000 Dr; extra CRJ R500; extra CPJ R1 200. The adjusted balance is ...',
                     ['R11 700 Dr', 'R10 700 Dr', 'R9 300 Dr', 'R8 300 Dr'], 2),
                    ('tf', 'A payment under-recorded in the CPJ is corrected by adding the difference to the CPJ.', True),
                    ('mcq', 'An overdraft appears in the business\'s Bank account as a ...',
                     ['debit balance', 'credit balance', 'asset', 'zero balance'], 1),
                ],
                'homework': {
                    'title': 'Update the journals',
                    'instructions': 'Use the information to calculate the adjusted Bank balance.',
                    'tasks': [
                        'Balance before adjustments R21 450 Dr. Items on the bank statement only: bank charges R420, debit order R1 300, interest received R65, EFT from debtor R2 800.',
                        'Error: a receipt of R940 was recorded in the CRJ as R490.',
                        'Show the additional CRJ total, CPJ total and the adjusted balance.',
                    ],
                    'marks': 12,
                },
            },
            {
                'title': 'Preparing the bank reconciliation statement',
                'minutes': 55,
                'objectives': [
                    'Learners will prepare a bank reconciliation statement in the correct format.',
                    'Learners will use the statement to calculate a missing bank statement balance.',
                    'Learners will identify internal control problems revealed by a reconciliation.',
                ],
                'notes': (
                    '<p>After the Cash Journals are updated, the only remaining differences are '
                    '<strong>timing differences</strong> (outstanding deposits and outstanding payments) and '
                    '<strong>bank errors</strong>. These are shown on the <strong>bank reconciliation '
                    'statement</strong>, which starts with the bank statement balance and ends with the adjusted '
                    'Bank account balance.</p>'
                    '<p><strong>Format (with Debit and Credit columns):</strong></p>'
                    '<ul>'
                    '<li>Balance per bank statement — Credit column if favourable (Debit if overdrawn).</li>'
                    '<li><strong>Outstanding deposits</strong> — Credit column (the bank will still add them).</li>'
                    '<li><strong>Outstanding payments</strong> — Debit column (the bank will still deduct them).</li>'
                    '<li>Balance per Bank account — Debit column if favourable (Credit if overdrawn).</li>'
                    '</ul>'
                    '<p>The two columns must have <strong>equal totals</strong>.</p>'
                    '<p><strong>Internal control:</strong> outstanding deposits older than a few days, or the '
                    'same deposit outstanding for two months, suggest that cash is being held back or stolen. '
                    'Outstanding payments that are very old should be investigated. Duties of receiving money, '
                    'recording it and reconciling the bank should be <em>divided</em> between different staff.</p>'
                ),
                'key_terms': [
                    ('Bank reconciliation statement', 'A statement that reconciles the bank statement balance with the Bank account balance.'),
                    ('Outstanding payment', 'A payment recorded in the CPJ that the bank has not yet processed.'),
                    ('Division of duties', 'Giving different people different tasks so that one person cannot commit and hide fraud.'),
                ],
                'example': {
                    'title': 'Worked example: Bank reconciliation statement of Nala Traders on 31 January',
                    'html': (
                        '<p>Adjusted Bank account balance: R12 590 (Dr). Outstanding deposit: R4 000. Outstanding '
                        'EFT payment: R2 230. Bank statement balance: R10 820 (Cr, favourable).</p>'
                        '<ul>'
                        '<li>Credit balance per bank statement — <strong>Cr R10 820</strong></li>'
                        '<li>Credit outstanding deposit — <strong>Cr R4 000</strong></li>'
                        '<li>Debit outstanding EFT payment — <strong>Dr R2 230</strong></li>'
                        '<li>Debit balance per Bank account — <strong>Dr R12 590</strong></li>'
                        '</ul>'
                        '<p><strong>Totals:</strong> Dr 2 230 + 12 590 = <strong>R14 820</strong>; '
                        'Cr 10 820 + 4 000 = <strong>R14 820</strong>. The statement balances.</p>'
                        '<p><em>Reverse calculation:</em> Bank statement balance = Bank account 12 590 − '
                        'outstanding deposit 4 000 + outstanding payment 2 230 = <strong>R10 820</strong>.</p>'
                    ),
                },
                'video': {'id': 'L4ClQyExIfg', 'title': 'Gr 11 - Bank Reconciliation - Activity 1', 'channel': 'JuniorTukkie at the University of Pretoria', 'minutes': 15},
                'worksheet': {
                    'instructions': 'Prepare bank reconciliation statements using Debit and Credit columns. Show all workings.',
                    'exercises': [
                        '1. Adjusted Bank account R9 750 (Dr). Outstanding deposit R2 500. Outstanding EFT payment R1 180. Calculate the bank statement balance.',
                        '2. Prepare the bank reconciliation statement for Question 1.',
                        '3. Bank statement R18 400 (Cr). Outstanding deposit R3 300. Outstanding payments R950 and R2 650. Calculate the Bank account balance and prepare the statement.',
                        '4. A deposit of R6 000 has been outstanding for 18 days. Explain why this is a concern and what the owner should do.',
                        '5. Suggest TWO internal control measures for handling cash receipts.',
                    ],
                },
                'quiz': [
                    ('mcq', 'On the bank reconciliation statement, an outstanding deposit is shown in the ...',
                     ['Debit column', 'Credit column', 'CPJ', 'General Journal'], 1),
                    ('mcq', 'Bank account R7 000 Dr, outstanding deposit R1 000, outstanding payment R500. Bank statement balance?',
                     ['R6 500 Cr', 'R8 500 Cr', 'R7 500 Cr', 'R5 500 Cr'], 0),
                    ('tf', 'Bank charges are shown on the bank reconciliation statement after the journals have been updated.', False),
                    ('mcq', 'A deposit outstanding for several weeks may indicate ...',
                     ['possible theft or poor control of cash', 'good internal control', 'a bank charge', 'a debit order'], 0),
                ],
                'homework': {
                    'title': 'Full bank reconciliation',
                    'instructions': 'Complete the full process for Zola Traders on 28 February.',
                    'tasks': [
                        'Bank account before adjustments R14 200 Dr. Bank statement only: bank charges R380, debit order R1 250, interest received R90.',
                        'Calculate the adjusted Bank balance.',
                        'Outstanding deposit R3 500; outstanding EFT payment R1 640. Calculate the bank statement balance and prepare the bank reconciliation statement.',
                    ],
                    'marks': 20,
                },
            },
        ],
    },
    (12, 'ACC'): {
        'topic': 'Companies: concepts, unique ledger accounts and notes',
        'caps': 'Accounting Grade 12, Term 1 — Financial accounting of companies: company concepts '
                '(Companies Act 71 of 2008), unique ledger accounts (ordinary share capital, retained '
                'income, dividends, income tax/SARS), and notes to the financial statements',
        'summary': 'Learners revise the nature of companies, record transactions in the ledger accounts '
                   'unique to companies, and prepare the ordinary share capital and retained income notes.',
        'days': [
            {
                'title': 'Company concepts and the Companies Act',
                'minutes': 50,
                'objectives': [
                    'Learners will explain the characteristics of a company in terms of the Companies Act 71 of 2008.',
                    'Learners will distinguish between authorised and issued share capital.',
                    'Learners will explain the roles of shareholders, directors and the auditor.',
                ],
                'notes': (
                    '<p>A <strong>company</strong> is a business registered under the <strong>Companies Act 71 of '
                    '2008</strong> with the Companies and Intellectual Property Commission (CIPC).</p>'
                    '<ul>'
                    '<li>It is a <strong>separate legal entity</strong>: it can own property, sue and be sued, and '
                    'continues to exist when shareholders change (<em>continuity</em>).</li>'
                    '<li>Owners are <strong>shareholders</strong> who have <strong>limited liability</strong> — they '
                    'can lose only what they paid for their shares.</li>'
                    '<li>A company is managed by <strong>directors</strong>, elected by shareholders at the '
                    '<strong>Annual General Meeting (AGM)</strong>.</li>'
                    '<li>Its founding document is the <strong>Memorandum of Incorporation (MOI)</strong>.</li>'
                    '<li>A public company (Ltd) can sell shares to the public, e.g. on the JSE; a private company '
                    '(Pty) Ltd cannot.</li>'
                    '</ul>'
                    '<p><strong>Shares:</strong> The MOI states the <strong>authorised share capital</strong> — the '
                    'maximum number of shares the company may issue. <strong>Issued share capital</strong> is the '
                    'number actually sold. Shares are <em>no par value</em> shares: they are issued at whatever '
                    'price the directors decide, and the full amount received goes to Ordinary share capital.</p>'
                    '<p>Shareholders earn <strong>dividends</strong> (a share of profit). Companies pay '
                    '<strong>income tax</strong> to SARS (currently 27% of net profit before tax). Public companies '
                    'must be audited by an <strong>independent external auditor</strong>.</p>'
                ),
                'key_terms': [
                    ('Limited liability', 'Shareholders can lose only the amount they invested in shares.'),
                    ('Authorised shares', 'The maximum number of shares a company may issue, as stated in the MOI.'),
                    ('Issued shares', 'The shares actually sold to shareholders.'),
                    ('Dividend', 'The part of profit distributed to shareholders.'),
                ],
                'example': {
                    'title': 'Worked example: issuing shares',
                    'html': (
                        '<p>Bheka Ltd is authorised to issue <strong>1 000 000</strong> ordinary shares. On 1 March '
                        '2025, <strong>600 000</strong> shares were in issue for R3 000 000 (average R5.00 each).</p>'
                        '<p>On 1 June 2025 the directors issued another <strong>100 000 shares at R6.50</strong>.</p>'
                        '<ol>'
                        '<li>Amount received = 100 000 × R6.50 = <strong>R650 000</strong>.</li>'
                        '<li>Entry: Bank (A) +650 000 | Ordinary share capital (OE) +650 000.</li>'
                        '<li>Shares now in issue = 600 000 + 100 000 = <strong>700 000</strong>.</li>'
                        '<li>Shares still available to issue = 1 000 000 − 700 000 = <strong>300 000</strong>.</li>'
                        '<li>Ordinary share capital = 3 000 000 + 650 000 = <strong>R3 650 000</strong>.</li>'
                        '</ol>'
                    ),
                },
                'video': {'id': '4noFjPHVVaw', 'title': '1. Theory of Companies - Shares Issued', 'channel': 'Like2Understand', 'minutes': 10},
                'worksheet': {
                    'instructions': 'Answer the theory and calculation questions.',
                    'exercises': [
                        '1. Explain what is meant by a "separate legal entity".',
                        '2. Explain limited liability and why it encourages people to invest.',
                        '3. Distinguish between authorised and issued share capital.',
                        '4. Who elects the directors and at which meeting?',
                        '5. A company issued 250 000 shares at R4.80 each. Calculate the amount received.',
                        '6. Authorised shares 2 000 000; issued 1 350 000. How many more shares may be issued?',
                        '7. Why is an independent audit important to shareholders?',
                    ],
                },
                'quiz': [
                    ('mcq', 'Which Act governs companies in South Africa?',
                     ['Companies Act 71 of 2008', 'Close Corporations Act 69 of 1984', 'Labour Relations Act', 'Consumer Protection Act'], 0),
                    ('mcq', 'The maximum number of shares a company may issue is its ...',
                     ['issued share capital', 'authorised share capital', 'retained income', 'dividend'], 1),
                    ('tf', 'Shareholders of a company have limited liability.', True),
                    ('mcq', '200 000 shares issued at R7.25 each brings in ...', ['R1 450 000', 'R145 000', 'R14 500 000', 'R725 000'], 0),
                ],
                'homework': {
                    'title': 'Company concepts',
                    'instructions': 'Answer in full sentences and show calculations.',
                    'tasks': [
                        'Compare a sole trader and a company under: liability, continuity, management, taxation.',
                        'Lindi Ltd is authorised to issue 800 000 shares; 500 000 are in issue for R2 500 000. It issues 120 000 more at R6.20. Calculate the new ordinary share capital and the number of unissued shares.',
                    ],
                    'marks': 15,
                },
            },
            {
                'title': 'Ledger accounts unique to companies',
                'minutes': 55,
                'objectives': [
                    'Learners will record entries in the Ordinary share capital, Retained income, Ordinary share dividends, Shareholders for dividends and SARS (Income tax) accounts.',
                    'Learners will calculate income tax payable or receivable.',
                    'Learners will explain the difference between interim and final dividends.',
                ],
                'notes': (
                    '<p>Companies use several accounts that a sole trader does not have:</p>'
                    '<ul>'
                    '<li><strong>Ordinary share capital</strong> (OE): credited with the amount received when '
                    'shares are issued.</li>'
                    '<li><strong>Retained income</strong> (OE): profits kept in the company and not paid out as '
                    'dividends. At year-end the net profit after tax is transferred here and dividends are '
                    'deducted.</li>'
                    '<li><strong>Income tax</strong> (expense): the tax on the company\'s profit for the year.</li>'
                    '<li><strong>SARS (Income tax)</strong> (liability or asset): companies pay '
                    '<em>provisional tax</em> during the year. If the final tax is more than the payments, the '
                    'balance is a liability (<strong>SARS: income tax payable</strong>); if less, SARS owes the '
                    'company (<strong>receivable</strong>).</li>'
                    '<li><strong>Ordinary share dividends</strong> (distribution of profit): records '
                    '<em>interim dividends</em> (paid during the year) and <em>final dividends</em> (declared at '
                    'year-end).</li>'
                    '<li><strong>Shareholders for dividends</strong> (current liability): the final dividend '
                    'declared but not yet paid.</li>'
                    '</ul>'
                    '<p>Dividends are calculated as <strong>number of shares × cents per share</strong>.</p>'
                ),
                'key_terms': [
                    ('Retained income', 'Accumulated profits not distributed as dividends.'),
                    ('Provisional tax', 'Income tax paid in advance during the year, based on estimated profit.'),
                    ('Interim dividend', 'A dividend paid during the financial year.'),
                    ('Final dividend', 'A dividend declared at the end of the financial year and paid later.'),
                ],
                'example': {
                    'title': 'Worked example: Bheka Ltd, year ended 28 February 2026',
                    'html': (
                        '<p><strong>Income tax:</strong> Net profit before tax R1 600 000; tax rate 27%.</p>'
                        '<ul>'
                        '<li>Income tax = 1 600 000 × 27% = <strong>R432 000</strong></li>'
                        '<li>Provisional tax paid during the year = R400 000</li>'
                        '<li>SARS: income tax payable = 432 000 − 400 000 = <strong>R32 000</strong> (current liability)</li>'
                        '<li>Net profit after tax = 1 600 000 − 432 000 = <strong>R1 168 000</strong></li>'
                        '</ul>'
                        '<p><strong>Dividends</strong> (700 000 shares in issue):</p>'
                        '<ul>'
                        '<li>Interim dividend 20 cents per share = 700 000 × R0.20 = <strong>R140 000</strong> (paid: '
                        'Ordinary share dividends Dr / Bank Cr)</li>'
                        '<li>Final dividend 30 cents per share = 700 000 × R0.30 = <strong>R210 000</strong> (declared: '
                        'Ordinary share dividends Dr / Shareholders for dividends Cr)</li>'
                        '<li>Total dividends = <strong>R350 000</strong>, closed off to Retained income.</li>'
                        '</ul>'
                    ),
                },
                'video': {'id': '2mL24kw09ms', 'title': 'Gr 12 Accounting - Companies - Issuing of Shares', 'channel': 'JuniorTukkie at the University of Pretoria', 'minutes': 15},
                'worksheet': {
                    'instructions': 'Calculate the amounts and name the accounts debited and credited.',
                    'exercises': [
                        '1. Net profit before tax R940 000, tax rate 27%. Calculate the income tax and net profit after tax.',
                        '2. Provisional tax paid R270 000; income tax for the year R253 800. Is there an amount payable to or receivable from SARS? How much?',
                        '3. 450 000 shares in issue. Interim dividend 15 cents per share. Calculate and name the accounts.',
                        '4. Final dividend of 25 cents per share declared on 450 000 shares. Calculate and name the accounts.',
                        '5. Explain why Shareholders for dividends is a current liability.',
                        '6. Explain the difference between the Income tax account and the SARS (Income tax) account.',
                    ],
                },
                'quiz': [
                    ('mcq', 'A final dividend declared but not paid is recorded in which liability account?',
                     ['SARS (Income tax)', 'Shareholders for dividends', 'Retained income', 'Ordinary share capital'], 1),
                    ('mcq', 'Net profit before tax R500 000 at 27% gives income tax of ...', ['R135 000', 'R365 000', 'R27 000', 'R50 000'], 0),
                    ('tf', 'If provisional tax payments exceed the final tax, SARS owes the company money.', True),
                    ('mcq', '800 000 shares × 12 cents per share = ...',
                     ['R9 600', 'R12 000', 'R960 000', 'R96 000'], 3),
                ],
                'homework': {
                    'title': 'Company ledger accounts',
                    'instructions': 'Use the information for Sibu Ltd (year end 28 February 2026).',
                    'tasks': [
                        'Net profit before tax R1 200 000; tax rate 27%; provisional tax paid R300 000. Calculate income tax and the amount due to/from SARS.',
                        '600 000 shares in issue: interim dividend 18 cents paid; final dividend 32 cents declared. Calculate both dividends.',
                        'Explain how dividends affect retained income.',
                    ],
                    'marks': 15,
                },
            },
            {
                'title': 'Notes: ordinary share capital and retained income',
                'minutes': 55,
                'objectives': [
                    'Learners will prepare the ordinary share capital note.',
                    'Learners will prepare the retained income note.',
                    'Learners will link the notes to the equity section of the Statement of Financial Position.',
                ],
                'notes': (
                    '<p>The <strong>Statement of Financial Position</strong> shows only totals. The details are '
                    'given in <strong>notes to the financial statements</strong>, as required by IFRS and the '
                    'Companies Act.</p>'
                    '<p><strong>Ordinary share capital note</strong> shows:</p>'
                    '<ul>'
                    '<li><strong>Authorised:</strong> the number of ordinary shares the company may issue.</li>'
                    '<li><strong>Issued:</strong> shares in issue at the beginning of the year (number and amount), '
                    'plus shares issued during the year, minus any shares bought back, giving the shares in issue '
                    'at year-end.</li>'
                    '</ul>'
                    '<p><strong>Retained income note</strong> shows:</p>'
                    '<ul>'
                    '<li>Balance at the beginning of the year</li>'
                    '<li><strong>+ Net profit after tax</strong></li>'
                    '<li><strong>− Ordinary share dividends</strong> (interim paid and final declared)</li>'
                    '<li>= Balance at the end of the year</li>'
                    '</ul>'
                    '<p><strong>Shareholders\' equity</strong> on the Statement of Financial Position = '
                    'Ordinary share capital + Retained income. The Statement of Financial Position must still '
                    'balance: total assets = shareholders\' equity + liabilities.</p>'
                ),
                'key_terms': [
                    ('Notes to the financial statements', 'Detailed explanations supporting amounts in the financial statements.'),
                    ('Shareholders\' equity', 'Ordinary share capital plus retained income.'),
                    ('IFRS', 'International Financial Reporting Standards, the global accounting standards companies follow.'),
                ],
                'example': {
                    'title': 'Worked example: Bheka Ltd notes on 28 February 2026',
                    'html': (
                        '<p><strong>1. Ordinary share capital</strong></p>'
                        '<ul>'
                        '<li>Authorised: 1 000 000 ordinary shares</li>'
                        '<li>Issued: 600 000 shares in issue on 1 March 2025 — R3 000 000</li>'
                        '<li>100 000 shares issued during the year at R6.50 — R650 000</li>'
                        '<li>700 000 shares in issue on 28 February 2026 — <strong>R3 650 000</strong></li>'
                        '</ul>'
                        '<p><strong>2. Retained income</strong></p>'
                        '<ul>'
                        '<li>Balance on 1 March 2025 — R820 000</li>'
                        '<li>Net profit after tax — R1 168 000</li>'
                        '<li>Ordinary share dividends — (R350 000): interim R140 000, final R210 000</li>'
                        '<li>Balance on 28 February 2026 — <strong>R1 638 000</strong></li>'
                        '</ul>'
                        '<p>Check: 820 000 + 1 168 000 − 350 000 = 1 638 000.</p>'
                        '<p><strong>Shareholders\' equity</strong> = 3 650 000 + 1 638 000 = <strong>R5 288 000</strong>.</p>'
                    ),
                },
                'video': {'id': 'sRPikm-zhPc', 'title': 'Grade 12 Accounting Term 1 | Ordinary share & Retained Income Notes Part 1 of 2026', 'channel': 'Accounting Solution SA', 'minutes': 20},
                'worksheet': {
                    'instructions': 'Prepare the notes for Thuli Ltd for the year ended 28 February 2026. Show workings.',
                    'exercises': [
                        '1. Authorised share capital: 1 500 000 ordinary shares.',
                        '2. On 1 March 2025: 800 000 shares in issue for R4 000 000.',
                        '3. On 1 September 2025: 150 000 additional shares issued at R5.80 each.',
                        '4. Retained income on 1 March 2025: R640 000. Net profit before tax R1 100 000; tax rate 27%.',
                        '5. Interim dividend paid R190 000; final dividend declared 25 cents per share on all shares in issue at year end.',
                        '6. Prepare the ordinary share capital note and the retained income note.',
                        '7. Calculate total shareholders\' equity.',
                    ],
                },
                'quiz': [
                    ('mcq', 'Which item is ADDED in the retained income note?',
                     ['Interim dividends', 'Final dividends', 'Net profit after tax', 'Income tax paid'], 2),
                    ('mcq', 'Opening retained income R300 000, net profit after tax R500 000, dividends R200 000. Closing balance?',
                     ['R1 000 000', 'R600 000', 'R400 000', 'R800 000'], 1),
                    ('tf', 'Shareholders\' equity consists of ordinary share capital and retained income.', True),
                    ('mcq', 'Where is authorised share capital disclosed?',
                     ['In the Income Statement', 'In the Cash Payments Journal', 'In the ordinary share capital note', 'In the retained income note'], 2),
                ],
                'homework': {
                    'title': 'Equity notes',
                    'instructions': 'Complete the notes and answer the question.',
                    'tasks': [
                        'Finish the worksheet notes for Thuli Ltd if not completed in class.',
                        'A shareholder says: "The company made R803 000 profit after tax, so it should pay all of it as dividends." Give TWO reasons why directors retain part of the profit.',
                    ],
                    'marks': 20,
                },
            },
        ],
    },
    # --------------------------------------------------------- BUSINESS STUDIES
    (10, 'BUS-STUD'): {
        'topic': 'Micro, market and macro environments',
        'caps': 'Business Studies Grade 10, Term 1, Business environments — the micro, market and '
                'macro environments: meaning, components, and the extent of control a business has '
                'over each environment',
        'summary': 'Learners identify the three business environments, their components, and how much '
                   'control a business has over each.',
        'days': [
            {
                'title': 'The three business environments',
                'minutes': 45,
                'objectives': [
                    'Learners will define the term "business environment".',
                    'Learners will name the three business environments and give a short description of each.',
                    'Learners will explain the extent of control a business has over each environment.',
                ],
                'notes': (
                    '<p>The <strong>business environment</strong> is everything inside and outside a business '
                    'that influences how it operates and how successful it is. Business Studies divides it into '
                    '<strong>three environments</strong>:</p>'
                    '<ol>'
                    '<li><strong>Micro environment</strong> — the <em>internal</em> environment: the business '
                    'itself, its vision and mission, organisational culture and structure, management and '
                    'leadership, resources and its business functions. The business has <strong>full '
                    'control</strong> over it.</li>'
                    '<li><strong>Market environment</strong> — the environment <em>immediately outside</em> the '
                    'business, in which it competes: consumers, suppliers, competitors, intermediaries, civil '
                    'society and regulators. The business has <strong>limited control</strong> but can '
                    '<em>influence</em> it, e.g. through marketing or negotiation.</li>'
                    '<li><strong>Macro environment</strong> — the wider <em>external</em> environment that '
                    'affects all businesses: political, economic, social, technological, legal, '
                    'environmental (physical) and international factors (PESTLE). The business has '
                    '<strong>no control</strong> over it and must <em>adapt</em>.</li>'
                    '</ol>'
                    '<p>The three environments are <strong>interrelated</strong>: a change in one, such as a '
                    'rise in the interest rate (macro), affects consumers\' spending (market) and the '
                    'business\'s financial planning (micro).</p>'
                ),
                'key_terms': [
                    ('Business environment', 'All internal and external factors that influence a business.'),
                    ('Micro environment', 'The internal environment of the business, over which it has full control.'),
                    ('Market environment', 'The environment just outside the business where it competes; limited control.'),
                    ('Macro environment', 'The wider external environment; the business has no control over it.'),
                ],
                'example': {
                    'title': 'Case study activity: Mpho\'s Bakery',
                    'html': (
                        '<p>Classify each factor as micro, market or macro, and state the extent of control:</p>'
                        '<ul>'
                        '<li>Mpho decides to open the bakery at 06:00 — <strong>micro</strong> (full control)</li>'
                        '<li>A new bakery opens across the road — <strong>market</strong> (competitor; limited control)</li>'
                        '<li>The price of wheat rises because of drought — <strong>macro</strong> (environmental/economic; no control)</li>'
                        '<li>The flour supplier delivers late — <strong>market</strong> (supplier; limited control)</li>'
                        '<li>The government increases VAT — <strong>macro</strong> (political/legal; no control)</li>'
                        '<li>Staff are not motivated — <strong>micro</strong> (human resources; full control)</li>'
                        '</ul>'
                    ),
                },
                'video': {'id': '7IZBdkCEaec', 'title': 'Types of Business Environments – Grade 10-12 Business Studies', 'channel': 'Teacher Ilona Smith', 'minutes': 10},
                'worksheet': {
                    'instructions': 'Answer the questions on the business environments.',
                    'exercises': [
                        '1. Define the term business environment.',
                        '2. Name the three business environments.',
                        '3. Explain the extent of control a business has over each environment.',
                        '4. Classify: (a) a strike by workers of the business; (b) load shedding; (c) a new competitor; (d) poor management.',
                        '5. Classify: (e) customers prefer online shopping; (f) an increase in the fuel price; (g) a change in the company\'s mission statement.',
                        '6. Give an example to show how the three environments are interrelated.',
                    ],
                },
                'quiz': [
                    ('mcq', 'Over which environment does a business have full control?', ['Micro', 'Market', 'Macro', 'International'], 0),
                    ('mcq', 'A competitor lowering its prices is part of the ...',
                     ['micro environment', 'legal environment only', 'macro environment', 'market environment'], 3),
                    ('tf', 'A business has no control over the macro environment.', True),
                    ('mcq', 'An increase in interest rates by the Reserve Bank is a ... factor.', ['micro', 'market', 'macro', 'internal'], 2),
                ],
                'homework': {
                    'title': 'Environments in my community',
                    'instructions': 'Choose a business in your community (e.g. a spaza shop, hair salon or garage).',
                    'tasks': [
                        'Name two factors from each of the three environments that affect this business.',
                        'For each factor, state the extent of control the business has.',
                    ],
                    'marks': 12,
                },
            },
            {
                'title': 'The micro environment: components and business functions',
                'minutes': 45,
                'objectives': [
                    'Learners will name and explain the components of the micro environment.',
                    'Learners will name the eight business functions.',
                    'Learners will explain the difference between a vision and a mission statement.',
                ],
                'notes': (
                    '<p>The <strong>micro environment</strong> is the business itself. Its components are:</p>'
                    '<ul>'
                    '<li><strong>Vision and mission statement:</strong> the <em>vision</em> describes what the '
                    'business wants to become in the future; the <em>mission</em> describes how it will achieve '
                    'the vision (its purpose and activities).</li>'
                    '<li><strong>Organisational goals and objectives:</strong> specific targets, e.g. "increase '
                    'sales by 10% this year".</li>'
                    '<li><strong>Organisational culture:</strong> the shared values and behaviour of employees.</li>'
                    '<li><strong>Organisational structure:</strong> how authority and tasks are arranged '
                    '(an organogram).</li>'
                    '<li><strong>Management and leadership:</strong> planning, organising, leading and controlling.</li>'
                    '<li><strong>Resources:</strong> physical, human, financial and technological resources.</li>'
                    '</ul>'
                    '<p>The <strong>eight business functions</strong> are:</p>'
                    '<ol>'
                    '<li>General management</li><li>Purchasing</li><li>Production</li><li>Marketing</li>'
                    '<li>Financial</li><li>Human resources</li><li>Public relations</li><li>Administration</li>'
                    '</ol>'
                    '<p>All the functions must work together. For example, if marketing increases sales, '
                    'production must make more and purchasing must buy more raw materials.</p>'
                ),
                'key_terms': [
                    ('Vision', 'A statement of what the business hopes to become in the future.'),
                    ('Mission statement', 'A statement of the purpose of the business and how it will achieve its vision.'),
                    ('Organisational culture', 'The shared values, beliefs and behaviour in a business.'),
                    ('Business function', 'A group of related activities performed in a business, e.g. marketing.'),
                ],
                'example': {
                    'title': 'Guided activity: which business function?',
                    'html': (
                        '<p>Identify the business function responsible for each activity at a clothing factory:</p>'
                        '<ul>'
                        '<li>Buying fabric from suppliers — <strong>purchasing</strong></li>'
                        '<li>Sewing shirts — <strong>production</strong></li>'
                        '<li>Advertising on social media — <strong>marketing</strong></li>'
                        '<li>Drawing up the budget — <strong>financial</strong></li>'
                        '<li>Recruiting a new machinist — <strong>human resources</strong></li>'
                        '<li>Sponsoring a school netball team — <strong>public relations</strong></li>'
                        '<li>Keeping records and filing invoices — <strong>administration</strong></li>'
                        '<li>Setting the overall strategy — <strong>general management</strong></li>'
                        '</ul>'
                    ),
                },
                'video': {'id': 'vwdEtYzFuPI', 'title': 'Grade 10 Business Studies: Micro Environment | Key Concepts', 'channel': 'Teacher Ilona Smith', 'minutes': 10},
                'worksheet': {
                    'instructions': 'Answer the questions on the micro environment.',
                    'exercises': [
                        '1. Distinguish between a vision and a mission statement.',
                        '2. Name SIX components of the micro environment.',
                        '3. List the EIGHT business functions.',
                        '4. Identify the business function: (a) paying salaries; (b) quality control of products; (c) a press release.',
                        '5. Explain why all business functions must work together.',
                        '6. Write a vision and a mission statement for a car-wash business.',
                    ],
                },
                'quiz': [
                    ('mcq', 'Which business function is responsible for recruiting staff?', ['Marketing', 'Human resources', 'Purchasing', 'Production'], 1),
                    ('mcq', 'What describes what a business wants to become in the future?',
                     ['Vision', 'Mission', 'Budget', 'Organogram'], 0),
                    ('tf', 'Organisational culture is part of the micro environment.', True),
                    ('mcq', 'Sponsoring a community event is mainly a ... activity.', ['public relations', 'production', 'administration', 'purchasing'], 0),
                ],
                'homework': {
                    'title': 'Business functions mind map',
                    'instructions': 'Draw a mind map.',
                    'tasks': [
                        'Draw a mind map of the eight business functions with two activities for each.',
                        'Write a vision and mission statement for a business you would like to start.',
                    ],
                    'marks': 15,
                },
            },
            {
                'title': 'The market and macro environments',
                'minutes': 45,
                'objectives': [
                    'Learners will explain the components of the market environment.',
                    'Learners will use PESTLE to describe the components of the macro environment.',
                    'Learners will suggest how a business can respond to challenges in each environment.',
                ],
                'notes': (
                    '<p><strong>Market environment</strong> components:</p>'
                    '<ul>'
                    '<li><strong>Consumers</strong> — people who buy the products; their needs and buying power '
                    'change.</li>'
                    '<li><strong>Suppliers</strong> — provide raw materials and goods.</li>'
                    '<li><strong>Intermediaries</strong> — wholesalers, retailers, agents and transport firms that '
                    'help get products to consumers.</li>'
                    '<li><strong>Competitors</strong> — other businesses selling similar or substitute products.</li>'
                    '<li><strong>Civil society</strong> — community organisations, NGOs and trade unions.</li>'
                    '<li><strong>Regulators</strong> — bodies such as the Competition Commission.</li>'
                    '</ul>'
                    '<p><strong>Macro environment</strong> components (<strong>PESTLE</strong>):</p>'
                    '<ul>'
                    '<li><strong>P</strong>olitical — government policies, stability.</li>'
                    '<li><strong>E</strong>conomic — inflation, interest rates, exchange rates, unemployment.</li>'
                    '<li><strong>S</strong>ocial — crime, HIV/Aids, demographics, changing lifestyles.</li>'
                    '<li><strong>T</strong>echnological — new technology, e-commerce, automation.</li>'
                    '<li><strong>L</strong>egal — legislation such as the Consumer Protection Act.</li>'
                    '<li><strong>E</strong>nvironmental (physical) — climate change, drought, pollution.</li>'
                    '</ul>'
                    '<p>International factors such as global recessions or trade agreements also form part of '
                    'the macro environment.</p>'
                ),
                'key_terms': [
                    ('Intermediary', 'A business that helps move products from producers to consumers.'),
                    ('Competitor', 'A business offering similar or substitute products to the same market.'),
                    ('PESTLE', 'Political, Economic, Social, Technological, Legal and Environmental factors.'),
                    ('Civil society', 'Organisations outside government and business, e.g. NGOs, trade unions.'),
                ],
                'example': {
                    'title': 'PESTLE analysis: a taxi business',
                    'html': (
                        '<ul>'
                        '<li><strong>Political:</strong> government policy on recapitalising the taxi fleet.</li>'
                        '<li><strong>Economic:</strong> higher fuel prices increase costs; higher interest rates '
                        'increase vehicle repayments.</li>'
                        '<li><strong>Social:</strong> commuters\' safety concerns; crime.</li>'
                        '<li><strong>Technological:</strong> cashless payment cards and ride-hailing apps.</li>'
                        '<li><strong>Legal:</strong> operating licences and road traffic regulations.</li>'
                        '<li><strong>Environmental:</strong> pressure to reduce vehicle emissions.</li>'
                        '</ul>'
                        '<p><em>Response:</em> The owner cannot control fuel prices, but can adapt — e.g. maintain '
                        'vehicles for better fuel efficiency and plan routes carefully.</p>'
                    ),
                },
                'video': {'id': 'uwPN0lndbwk', 'title': 'Macro Environment | Business studies', 'channel': 'Teacher Ilona Smith', 'minutes': 10},
                'worksheet': {
                    'instructions': 'Answer the questions on the market and macro environments.',
                    'exercises': [
                        '1. Name FIVE components of the market environment.',
                        '2. Explain the role of intermediaries, with an example.',
                        '3. What does PESTLE stand for?',
                        '4. Give ONE example of each PESTLE factor that could affect a supermarket.',
                        '5. Explain why a business cannot control the macro environment.',
                        '6. Suggest TWO ways a business can respond to strong competition.',
                    ],
                },
                'quiz': [
                    ('mcq', 'Which is a component of the market environment?',
                     ['Inflation', 'Organisational culture', 'Suppliers', 'Legislation'], 2),
                    ('mcq', 'In PESTLE, the "T" stands for ...', ['Trade', 'Technological', 'Taxation', 'Transport'], 1),
                    ('tf', 'Wholesalers and retailers are examples of intermediaries.', True),
                    ('mcq', 'A drought affecting crop prices is an example of a(n) ... factor.', ['environmental', 'micro', 'consumer', 'administrative'], 0),
                ],
                'homework': {
                    'title': 'PESTLE analysis',
                    'instructions': 'Choose a well-known South African business.',
                    'tasks': [
                        'Do a PESTLE analysis with one factor under each heading.',
                        'Choose the factor that poses the biggest challenge and suggest how the business could adapt.',
                    ],
                    'marks': 15,
                },
            },
        ],
    },
    (11, 'BUS-STUD'): {
        'topic': 'Influences on business environments',
        'caps': 'Business Studies Grade 11, Term 1, Business environments — influences on the business '
                'environments: components of the micro, market and macro environments, the extent of '
                'control, the interrelationship between the environments, and challenges they present',
        'summary': 'Learners analyse how the components of each business environment influence business '
                   'operations, how much control a business has, and how the environments interact.',
        'days': [
            {
                'title': 'Influences of the micro environment',
                'minutes': 50,
                'objectives': [
                    'Learners will explain how components of the micro environment influence a business.',
                    'Learners will relate the business functions to business success or failure.',
                    'Learners will explain why a business has full control over the micro environment.',
                ],
                'notes': (
                    '<p>In Grade 10 you identified the three environments. In Grade 11 we analyse their '
                    '<strong>influence</strong> — how each component can help or hinder a business.</p>'
                    '<p><strong>Micro environment influences</strong> (full control):</p>'
                    '<ul>'
                    '<li><strong>Vision, mission and objectives:</strong> unclear goals lead to wasted resources.</li>'
                    '<li><strong>Organisational culture:</strong> a positive culture improves productivity; a toxic '
                    'culture leads to high staff turnover.</li>'
                    '<li><strong>Management and leadership:</strong> poor planning or decision-making can lead to '
                    'losses and even business failure.</li>'
                    '<li><strong>Organisational structure:</strong> unclear lines of authority cause confusion and '
                    'delays.</li>'
                    '<li><strong>Resources:</strong> a shortage of skilled staff, capital or equipment limits growth.</li>'
                    '<li><strong>Business functions:</strong> each can create challenges — e.g. poor quality '
                    'control (production), cash-flow problems (financial), low staff morale or strikes '
                    '(human resources), or a poor public image (public relations).</li>'
                    '</ul>'
                    '<p>Because these factors are inside the business, management can <strong>control</strong> '
                    'them through strategies such as training, better planning, improved communication and '
                    'restructuring.</p>'
                ),
                'key_terms': [
                    ('Influence', 'The effect a factor has on a business\'s operations and success.'),
                    ('Staff turnover', 'The rate at which employees leave and must be replaced.'),
                    ('Cash flow', 'The movement of money into and out of a business.'),
                ],
                'example': {
                    'title': 'Case study: Kasi Kicks (sneaker store)',
                    'html': (
                        '<p><em>Kasi Kicks has a strong brand, but managers often change priorities without telling '
                        'staff. Sales assistants are not trained on new products, and the store regularly runs out '
                        'of popular sizes because orders are placed late.</em></p>'
                        '<ol>'
                        '<li><strong>Management:</strong> poor communication — hold weekly staff meetings.</li>'
                        '<li><strong>Human resources:</strong> untrained staff — introduce product training.</li>'
                        '<li><strong>Purchasing:</strong> late orders cause stock-outs — use a stock-control system '
                        'with reorder levels.</li>'
                        '</ol>'
                        '<p>All three problems are in the <strong>micro environment</strong>, so the business has '
                        '<strong>full control</strong> to solve them.</p>'
                    ),
                },
                'video': {'id': 'zfMniqXBt-c', 'title': 'Grade 11 Business Studies Influences in Business Environments', 'channel': 'Teacher Ilona Smith', 'minutes': 10},
                'worksheet': {
                    'instructions': 'Answer the questions on the influences of the micro environment.',
                    'exercises': [
                        '1. Explain how organisational culture can influence a business positively and negatively.',
                        '2. Explain how poor management can lead to business failure.',
                        '3. Identify a challenge from each of the following functions: financial, production, marketing.',
                        '4. Why does a business have full control over its micro environment?',
                        '5. Suggest TWO strategies to deal with high staff turnover.',
                        '6. Read the Kasi Kicks case study and add ONE more problem and solution.',
                    ],
                },
                'quiz': [
                    ('mcq', 'Which is an influence from the micro environment?',
                     ['A rise in VAT', 'A recession', 'A new competitor', 'Low staff morale'], 3),
                    ('tf', 'A business has full control over the components of its micro environment.', True),
                    ('mcq', 'Poor quality control is a challenge of the ... function.', ['production', 'public relations', 'administration', 'legal'], 0),
                    ('mcq', 'Which strategy would best address poor communication between managers and staff?',
                     ['Hold regular staff meetings', 'Increase prices', 'Change suppliers', 'Lobby government'], 0),
                ],
                'homework': {
                    'title': 'Micro environment analysis',
                    'instructions': 'Use a business you know.',
                    'tasks': [
                        'Identify three micro-environment challenges the business faces.',
                        'Suggest a practical solution for each challenge.',
                    ],
                    'marks': 12,
                },
            },
            {
                'title': 'Influences of the market and macro environments',
                'minutes': 50,
                'objectives': [
                    'Learners will explain how consumers, suppliers, competitors and intermediaries influence a business.',
                    'Learners will explain how macro factors such as inflation, crime and technology influence a business.',
                    'Learners will distinguish between limited control and no control.',
                ],
                'notes': (
                    '<p><strong>Market environment</strong> (limited control — the business can influence it):</p>'
                    '<ul>'
                    '<li><strong>Consumers:</strong> changing tastes or lower income reduce demand. A business can '
                    'influence them through marketing and customer service.</li>'
                    '<li><strong>Suppliers:</strong> late deliveries, poor quality or price increases disrupt '
                    'production. The business can negotiate or find alternative suppliers.</li>'
                    '<li><strong>Competitors:</strong> lower prices or better products take market share.</li>'
                    '<li><strong>Intermediaries:</strong> wholesalers or retailers may demand bigger discounts.</li>'
                    '<li><strong>Civil society and regulators:</strong> community pressure or rules from bodies '
                    'such as the Competition Commission.</li>'
                    '</ul>'
                    '<p><strong>Macro environment</strong> (no control — the business must adapt):</p>'
                    '<ul>'
                    '<li><strong>Economic:</strong> inflation, interest rates, exchange rates and unemployment '
                    'affect costs and consumer spending.</li>'
                    '<li><strong>Social:</strong> crime increases security costs; HIV/Aids affects productivity; '
                    'inequality affects buying power.</li>'
                    '<li><strong>Technological:</strong> new technology can create opportunities (e-commerce) or '
                    'make products outdated.</li>'
                    '<li><strong>Political and legal:</strong> new laws, e.g. labour legislation, increase '
                    'compliance costs.</li>'
                    '<li><strong>Physical:</strong> load shedding, water shortages and climate change.</li>'
                    '<li><strong>International:</strong> global recessions or trade restrictions affect exports.</li>'
                    '</ul>'
                ),
                'key_terms': [
                    ('Market share', 'The percentage of total sales in a market made by one business.'),
                    ('Inflation', 'A sustained increase in the general price level.'),
                    ('Compliance', 'Obeying laws and regulations, which often has a cost.'),
                ],
                'example': {
                    'title': 'Guided analysis: a clothing retailer',
                    'html': (
                        '<p>For each factor, name the environment, the component and the extent of control:</p>'
                        '<ul>'
                        '<li>Customers buy more clothes online — <strong>market</strong>, consumers, '
                        '<em>limited control</em>. Response: open an online store.</li>'
                        '<li>The rand weakens against the US dollar, making imported fabric dearer — '
                        '<strong>macro</strong>, economic, <em>no control</em>. Response: use local suppliers.</li>'
                        '<li>A supplier delivers faulty stock — <strong>market</strong>, suppliers, <em>limited '
                        'control</em>. Response: enforce a service-level agreement.</li>'
                        '<li>Load shedding closes the store for hours — <strong>macro</strong>, physical/'
                        'infrastructure, <em>no control</em>. Response: install a generator or solar backup.</li>'
                        '</ul>'
                    ),
                },
                'video': {'id': '6oDy8ftCvac', 'title': 'Influences of the Business Environments | Grade 11 Business Studies FULL LESSON', 'channel': 'Teacher Ilona Smith', 'minutes': 15},
                'worksheet': {
                    'instructions': 'Answer the questions on the market and macro environments.',
                    'exercises': [
                        '1. Explain how competitors can influence a business.',
                        '2. Explain why a business has only limited control over its suppliers.',
                        '3. Explain how an increase in interest rates influences both the business and its consumers.',
                        '4. Discuss the influence of crime on businesses in South Africa.',
                        '5. Explain how technology can be both a threat and an opportunity.',
                        '6. Distinguish between "limited control" and "no control", with an example of each.',
                    ],
                },
                'quiz': [
                    ('mcq', 'A business has ... over the market environment.', ['full control', 'limited control', 'no control', 'legal control'], 1),
                    ('mcq', 'Which is a macro-environment factor?', ['Suppliers', 'Competitors', 'Exchange rates', 'Organisational culture'], 2),
                    ('tf', 'A business can influence consumers through marketing.', True),
                    ('mcq', 'Load shedding is an example of a challenge in the ... environment.', ['micro', 'market', 'macro', 'internal'], 2),
                ],
                'homework': {
                    'title': 'News analysis',
                    'instructions': 'Find a recent South African news article about a challenge facing businesses.',
                    'tasks': [
                        'Summarise the article in 3–4 sentences.',
                        'Identify the environment and component involved and the extent of control.',
                        'Suggest how affected businesses can adapt.',
                    ],
                    'marks': 12,
                },
            },
            {
                'title': 'The interrelationship between the business environments',
                'minutes': 50,
                'objectives': [
                    'Learners will explain how the three environments are interrelated.',
                    'Learners will trace the effect of a macro change through the market and micro environments.',
                    'Learners will apply their knowledge to a case study in exam format.',
                ],
                'notes': (
                    '<p>The three environments do not operate separately: a change in one environment causes '
                    'changes in the others. Managers must therefore constantly <strong>scan</strong> the '
                    'environments and adapt.</p>'
                    '<p><strong>Example of a chain reaction:</strong></p>'
                    '<ol>'
                    '<li><strong>Macro:</strong> the Reserve Bank increases the repo rate (economic factor).</li>'
                    '<li><strong>Market:</strong> consumers pay more on their loans and have less to spend; '
                    'competitors cut prices to attract customers.</li>'
                    '<li><strong>Micro:</strong> the business\'s sales fall, so the financial function revises '
                    'the budget, marketing runs promotions, and management may delay expansion plans.</li>'
                    '</ol>'
                    '<p>Changes can also move "outwards": a large business that adopts new technology (micro) '
                    'may change consumer expectations and force competitors to follow (market).</p>'
                    '<p><strong>Exam tip:</strong> In case-study questions, <em>quote</em> the line from the '
                    'case study, then <em>identify</em> the environment and component, and finally '
                    '<em>explain</em> its influence or suggest a solution.</p>'
                ),
                'key_terms': [
                    ('Interrelationship', 'The way changes in one environment affect the other environments.'),
                    ('Environmental scanning', 'Monitoring the business environments to identify opportunities and threats.'),
                    ('Repo rate', 'The interest rate at which the Reserve Bank lends money to commercial banks.'),
                ],
                'example': {
                    'title': 'Exam-style case study: Ubuntu Foods',
                    'html': (
                        '<p><em>Ubuntu Foods makes snacks. Recently the price of maize increased due to drought. '
                        'A large supermarket chain asked for a bigger discount. Ubuntu\'s managers have not '
                        'agreed on a plan, and staff are worried about job losses.</em></p>'
                        '<ul>'
                        '<li><strong>Quote:</strong> "price of maize increased due to drought" — <strong>macro</strong> '
                        '(physical/environmental), no control.</li>'
                        '<li><strong>Quote:</strong> "supermarket chain asked for a bigger discount" — '
                        '<strong>market</strong> (intermediary), limited control.</li>'
                        '<li><strong>Quote:</strong> "managers have not agreed on a plan" — <strong>micro</strong> '
                        '(management), full control.</li>'
                        '</ul>'
                        '<p><strong>Interrelationship:</strong> the drought (macro) raises costs, which weakens Ubuntu\'s '
                        'bargaining power with the supermarket (market), which creates pressure on management and '
                        'staff (micro).</p>'
                    ),
                },
                'video': {'id': 'qnQ0UPoA4Bo', 'title': 'Business Environments Interrelationship | Grade 10 | Business Studies', 'channel': 'Teacher Ilona Smith', 'minutes': 8},
                'worksheet': {
                    'instructions': 'Read the Ubuntu Foods case study and answer the questions.',
                    'exercises': [
                        '1. Quote THREE challenges from the case study and identify the business environment of each.',
                        '2. State the extent of control Ubuntu Foods has over each challenge.',
                        '3. Explain how the three challenges are interrelated.',
                        '4. Suggest ONE solution for each challenge.',
                        '5. Explain what environmental scanning is and why Ubuntu Foods should do it.',
                    ],
                },
                'quiz': [
                    ('tf', 'A change in the macro environment can affect the market and micro environments.', True),
                    ('mcq', 'In a case study, "The supplier increased its prices" refers to the ...',
                     ['micro environment', 'legal environment', 'macro environment', 'market environment'], 3),
                    ('mcq', 'What is environmental scanning?',
                     ['Cleaning the business premises', 'Monitoring the environments for opportunities and threats',
                      'Advertising on social media', 'Hiring new staff'], 1),
                    ('mcq', 'Which sequence shows a correct chain reaction?',
                     ['Repo rate rises > consumers spend less > sales fall',
                      'Sales fall > repo rate rises > consumers spend more',
                      'Consumers spend more > repo rate falls > sales fall',
                      'Sales rise > drought occurs > repo rate falls'], 0),
                ],
                'homework': {
                    'title': 'Interrelationship flow chart',
                    'instructions': 'Draw a flow chart.',
                    'tasks': [
                        'Choose ONE macro change (e.g. a fuel price increase) and show its effect on the market and micro environments of a bakery.',
                        'Write a paragraph suggesting how the bakery can adapt.',
                    ],
                    'marks': 15,
                },
            },
        ],
    },
    (12, 'BUS-STUD'): {
        'topic': 'Impact of recent legislation on business',
        'caps': 'Business Studies Grade 12, Term 1, Business environments — the impact of recent '
                'legislation on business: LRA, BCEA, EEA, SDA, BBBEE Act, COIDA, Consumer Protection Act '
                'and National Credit Act; purpose, provisions, impact and compliance',
        'summary': 'Learners study the purpose and key provisions of the main South African laws affecting '
                   'business, evaluate their positive and negative impact, and suggest how businesses can comply.',
        'days': [
            {
                'title': 'Labour legislation: LRA and BCEA',
                'minutes': 50,
                'objectives': [
                    'Learners will explain the purpose of the Labour Relations Act and the Basic Conditions of Employment Act.',
                    'Learners will outline key provisions of the BCEA.',
                    'Learners will evaluate the positive and negative impact of these Acts on businesses.',
                ],
                'notes': (
                    '<p>Since 1994 South Africa has passed laws to protect workers, promote fairness and '
                    'redress past inequality. Businesses must <strong>comply</strong> or face fines.</p>'
                    '<p><strong>Labour Relations Act (LRA), 66 of 1995</strong></p>'
                    '<ul>'
                    '<li>Gives workers the right to join <strong>trade unions</strong> and to <strong>strike</strong> '
                    '(protected strikes), and employers the right to lock out.</li>'
                    '<li>Promotes <strong>collective bargaining</strong> through bargaining councils and workplace forums.</li>'
                    '<li>Created the <strong>CCMA</strong> (Commission for Conciliation, Mediation and Arbitration) to '
                    'resolve disputes and protects workers against <strong>unfair dismissal</strong>.</li>'
                    '</ul>'
                    '<p><strong>Basic Conditions of Employment Act (BCEA), 75 of 1997</strong> sets minimum conditions:</p>'
                    '<ul>'
                    '<li>Maximum <strong>45 ordinary working hours</strong> per week; overtime limited to 10 hours '
                    'a week and paid at <strong>1.5 times</strong> the normal rate.</li>'
                    '<li>Annual leave of <strong>21 consecutive days</strong> per year; sick leave of '
                    '<strong>30 days in a 36-month cycle</strong>; <strong>4 consecutive months</strong> of '
                    'maternity leave; family responsibility leave.</li>'
                    '<li>Rules on notice periods, written particulars of employment and a ban on child labour '
                    '(under 15).</li>'
                    '</ul>'
                    '<p><strong>Impact:</strong> positive — fairer, more motivated workforce and fewer disputes; '
                    'negative — higher labour costs, less flexibility and time-consuming dispute procedures.</p>'
                ),
                'key_terms': [
                    ('CCMA', 'Commission for Conciliation, Mediation and Arbitration: resolves labour disputes.'),
                    ('Collective bargaining', 'Negotiation between employers and trade unions on wages and conditions.'),
                    ('Protected strike', 'A strike that follows the LRA procedures; strikers cannot be dismissed for striking.'),
                    ('Compliance', 'Obeying the requirements of the law.'),
                ],
                'example': {
                    'title': 'Scenario analysis: is the employer complying?',
                    'html': (
                        '<p><em>Zama works at a factory. She works 48 ordinary hours per week, gets 15 days\' annual '
                        'leave and is paid her normal rate for overtime.</em></p>'
                        '<ol>'
                        '<li>48 ordinary hours exceeds the BCEA maximum of <strong>45 hours</strong> — '
                        '<strong>not compliant</strong>.</li>'
                        '<li>15 days\' leave is less than <strong>21 consecutive days</strong> — '
                        '<strong>not compliant</strong>.</li>'
                        '<li>Overtime must be paid at <strong>1.5 times</strong> the normal rate — '
                        '<strong>not compliant</strong>.</li>'
                        '</ol>'
                        '<p><em>What can Zama do?</em> Raise a grievance internally; if unresolved, refer the dispute '
                        'to the Department of Employment and Labour or the CCMA.</p>'
                    ),
                },
                'video': {'id': 'ybR9NJ-6yZg', 'title': 'Grade 12 Term 1 | Business Studies | Labour Relations Act | Legislation', 'channel': 'Teacher Ilona Smith', 'minutes': 12},
                'worksheet': {
                    'instructions': 'Answer the questions on the LRA and BCEA.',
                    'exercises': [
                        '1. State the purpose of the Labour Relations Act.',
                        '2. Explain the role of the CCMA.',
                        '3. List FIVE provisions of the BCEA.',
                        '4. Discuss the positive impact of the BCEA on businesses.',
                        '5. Discuss the negative impact of the LRA on businesses.',
                        '6. Read the Zama scenario and identify THREE ways the employer contravenes the BCEA.',
                    ],
                },
                'quiz': [
                    ('mcq', 'What is the maximum number of ordinary working hours per week under the BCEA?', ['40', '45', '48', '50'], 1),
                    ('mcq', 'Which body resolves labour disputes through conciliation and arbitration?',
                     ['SARS', 'SETA', 'CCMA', 'CIPC'], 2),
                    ('tf', 'Under the BCEA, overtime must be paid at 1.5 times the normal rate.', True),
                    ('mcq', 'How much annual leave does the BCEA require?',
                     ['10 working days', '15 consecutive days', '21 consecutive days', '30 days'], 2),
                ],
                'homework': {
                    'title': 'Labour legislation impact',
                    'instructions': 'Answer in essay-style paragraphs.',
                    'tasks': [
                        'Explain four positive and four negative impacts of the BCEA on businesses.',
                        'Suggest two ways a business can comply with the BCEA.',
                    ],
                    'marks': 16,
                },
            },
            {
                'title': 'Transformation legislation: EEA, SDA and BBBEE',
                'minutes': 50,
                'objectives': [
                    'Learners will explain the purpose of the Employment Equity Act, Skills Development Act and BBBEE Act.',
                    'Learners will name the pillars of the BBBEE scorecard.',
                    'Learners will evaluate the impact of these Acts on businesses.',
                ],
                'notes': (
                    '<p><strong>Employment Equity Act (EEA), 55 of 1998</strong></p>'
                    '<ul>'
                    '<li>Prohibits <strong>unfair discrimination</strong> in the workplace (e.g. on race, gender, '
                    'disability, religion).</li>'
                    '<li>Requires designated employers to implement <strong>affirmative action</strong> for black '
                    'people, women and people with disabilities, and to submit an <strong>employment equity plan</strong> '
                    'and reports to the Department of Employment and Labour.</li>'
                    '</ul>'
                    '<p><strong>Skills Development Act (SDA), 97 of 1998</strong></p>'
                    '<ul>'
                    '<li>Aims to improve the skills of the workforce. Employers with a payroll of more than '
                    'R500 000 a year pay a <strong>skills development levy of 1%</strong> of payroll to SARS.</li>'
                    '<li><strong>SETAs</strong> (Sector Education and Training Authorities) use the levy to fund '
                    '<strong>learnerships</strong> and training; businesses can claim back part of the levy.</li>'
                    '</ul>'
                    '<p><strong>Broad-Based Black Economic Empowerment Act (BBBEE), 53 of 2003</strong> (amended 2013)</p>'
                    '<ul>'
                    '<li>Promotes meaningful economic participation of black people. Businesses are measured on a '
                    '<strong>scorecard</strong> with five pillars: <strong>ownership, management control, skills '
                    'development, enterprise and supplier development, and socio-economic development</strong>.</li>'
                    '<li>A good BBBEE level helps businesses win government tenders.</li>'
                    '</ul>'
                    '<p><strong>Impact:</strong> a more diverse, skilled workforce and access to tenders; but also '
                    'administrative costs, and risks such as "fronting" (falsely claiming black ownership).</p>'
                ),
                'key_terms': [
                    ('Affirmative action', 'Measures to ensure that previously disadvantaged groups have equal opportunities.'),
                    ('SETA', 'Sector Education and Training Authority, which manages training in an economic sector.'),
                    ('Learnership', 'A structured programme combining theory and workplace practice, leading to a qualification.'),
                    ('Fronting', 'Falsely presenting a business as BBBEE-compliant, e.g. using black people as token owners.'),
                ],
                'example': {
                    'title': 'Worked example: the skills development levy',
                    'html': (
                        '<p>Moyo Engineering has an annual payroll of <strong>R2 400 000</strong>.</p>'
                        '<ol>'
                        '<li>Is it liable? Payroll exceeds R500 000, so <strong>yes</strong>.</li>'
                        '<li>Levy = 1% × 2 400 000 = <strong>R24 000 per year</strong> (R2 000 per month), paid to SARS.</li>'
                        '<li>If Moyo submits a workplace skills plan and trains its staff, it can claim back part of '
                        'this levy from its SETA as a grant.</li>'
                        '</ol>'
                        '<p><em>Discuss:</em> How does training staff through a learnership also help Moyo\'s BBBEE '
                        'score? (It counts towards the <strong>skills development</strong> pillar.)</p>'
                    ),
                },
                'video': {'id': 'UnwzIwEmL9c', 'title': 'Broad Based Black Economic Empowerment Act | Grade 12 Term 1 | Business Studies | Legislation', 'channel': 'Teacher Ilona Smith', 'minutes': 12},
                'worksheet': {
                    'instructions': 'Answer the questions on the EEA, SDA and BBBEE Act.',
                    'exercises': [
                        '1. State TWO purposes of the Employment Equity Act.',
                        '2. Explain the role of SETAs.',
                        '3. Calculate the skills development levy for a business with an annual payroll of R1 800 000.',
                        '4. Name the FIVE pillars of BBBEE.',
                        '5. Discuss the positive impact of BBBEE on businesses.',
                        '6. What is fronting and why is it harmful?',
                    ],
                },
                'quiz': [
                    ('mcq', 'What percentage of payroll is paid as the skills development levy?', ['0.5%', '1%', '2%', '5%'], 1),
                    ('mcq', 'Which is a pillar of the BBBEE scorecard?', ['Overtime pay', 'Enterprise and supplier development', 'Consumer credit', 'Annual leave'], 1),
                    ('tf', 'The Employment Equity Act prohibits unfair discrimination in the workplace.', True),
                    ('mcq', 'Which bodies use the skills levy to fund training?', ['SETAs', 'Trade unions', 'The CCMA', 'The JSE'], 0),
                ],
                'homework': {
                    'title': 'BBBEE evaluation',
                    'instructions': 'Write a short essay (about 1 page).',
                    'tasks': [
                        'Introduce the BBBEE Act and its purpose.',
                        'Discuss three positive and three negative impacts of BBBEE on businesses.',
                        'Suggest ways businesses can comply with BBBEE.',
                    ],
                    'marks': 20,
                },
            },
            {
                'title': 'Consumer legislation and COIDA: CPA, NCA and COIDA',
                'minutes': 50,
                'objectives': [
                    'Learners will explain consumer rights under the Consumer Protection Act.',
                    'Learners will explain the purpose and key provisions of the National Credit Act.',
                    'Learners will explain the purpose of COIDA and how businesses comply with it.',
                ],
                'notes': (
                    '<p><strong>Consumer Protection Act (CPA), 68 of 2008</strong> protects consumers against '
                    'unfair business practices. Consumer rights include the right to:</p>'
                    '<ul>'
                    '<li>equality in the consumer market; privacy (e.g. blocking direct marketing); choice;</li>'
                    '<li>disclosure and information in plain, understandable language;</li>'
                    '<li>fair and responsible marketing; fair and honest dealing;</li>'
                    '<li>fair, just and reasonable terms; and <strong>fair value, good quality and safety</strong> — '
                    'defective goods may be returned within <strong>six months</strong> for repair, replacement or '
                    'refund. There is a <strong>five business day cooling-off period</strong> for direct-marketing sales.</li>'
                    '</ul>'
                    '<p><strong>National Credit Act (NCA), 34 of 2005</strong> regulates credit. Credit providers must '
                    'register with the <strong>National Credit Regulator</strong>, do an <strong>affordability '
                    'assessment</strong> before granting credit, and avoid <em>reckless lending</em>. Consumers have '
                    'the right to receive information about the cost of credit and to apply for debt counselling.</p>'
                    '<p><strong>Compensation for Occupational Injuries and Diseases Act (COIDA), 130 of 1993</strong> '
                    'provides compensation to employees injured or made ill at work. Employers register with the '
                    '<strong>Compensation Fund</strong> and pay annual contributions; employees cannot sue the '
                    'employer for these injuries but claim from the fund instead.</p>'
                ),
                'key_terms': [
                    ('Cooling-off period', 'A period in which a consumer may cancel a direct-marketing agreement without penalty.'),
                    ('Reckless lending', 'Granting credit without properly assessing whether the consumer can afford it.'),
                    ('Affordability assessment', 'A check of a consumer\'s income and expenses before credit is granted.'),
                    ('Compensation Fund', 'The fund under COIDA that compensates employees for work-related injuries and diseases.'),
                ],
                'example': {
                    'title': 'Scenario analysis: which law applies?',
                    'html': (
                        '<ul>'
                        '<li><em>Lerato buys a kettle that stops working after two months.</em> — <strong>CPA</strong>: '
                        'right to fair value, good quality and safety; she may return it within six months for '
                        'repair, replacement or refund.</li>'
                        '<li><em>A furniture store gives a R40 000 credit agreement to an unemployed customer without '
                        'checking income.</em> — <strong>NCA</strong>: reckless lending; no affordability assessment.</li>'
                        '<li><em>A worker\'s hand is injured by a machine.</em> — <strong>COIDA</strong>: the worker '
                        'claims compensation from the Compensation Fund.</li>'
                        '<li><em>A salesperson persuades Sipho at his home to buy a vacuum cleaner; he changes his mind '
                        'three business days later.</em> — <strong>CPA</strong>: he is within the five-business-day '
                        'cooling-off period.</li>'
                        '</ul>'
                    ),
                },
                'video': {'id': 'OnXJqeatQjU', 'title': 'Business studies grade 12 | Consumer Protection Act | Impact of Legislation', 'channel': 'Teacher Ilona Smith', 'minutes': 12},
                'worksheet': {
                    'instructions': 'Answer the questions on the CPA, NCA and COIDA.',
                    'exercises': [
                        '1. Name FIVE consumer rights in terms of the CPA.',
                        '2. Explain the cooling-off period.',
                        '3. State THREE provisions of the National Credit Act.',
                        '4. Explain what reckless lending is and how the NCA prevents it.',
                        '5. Explain the purpose of COIDA.',
                        '6. Discuss the negative impact of the CPA on businesses.',
                        '7. For each scenario in the class example, name the Act and the specific right or provision.',
                    ],
                },
                'quiz': [
                    ('mcq', 'Which Act protects consumers who buy defective goods?',
                     ['Consumer Protection Act', 'National Credit Act', 'Labour Relations Act', 'COIDA'], 0),
                    ('mcq', 'Credit providers must register with the ...',
                     ['National Credit Regulator', 'CCMA', 'Compensation Fund', 'SETA'], 0),
                    ('tf', 'COIDA allows employees to claim compensation for injuries suffered at work.', True),
                    ('mcq', 'How long is the cooling-off period for direct-marketing sales under the CPA?',
                     ['24 hours', 'Thirty days', 'Five business days', 'Six months'], 2),
                    ('tf', 'The NCA requires an affordability assessment before credit is granted.', True),
                ],
                'homework': {
                    'title': 'Legislation summary table',
                    'instructions': 'Create a summary table for revision.',
                    'tasks': [
                        'For the LRA, BCEA, EEA, SDA, BBBEE, CPA, NCA and COIDA, give: full name and number, purpose, one provision, one positive and one negative impact.',
                    ],
                    'marks': 16,
                },
            },
        ],
    },
    # ---------------------------------------------------------------- ECONOMICS
    (10, 'ECON'): {
        'topic': 'Basic concepts: the economic problem',
        'caps': 'Economics Grade 10, Term 1, Macroeconomics — Basic concepts: the economic problem '
                '(unlimited wants, scarce resources, choice), opportunity cost, the basic economic '
                'questions and production possibility curves',
        'summary': 'Learners explore why scarcity forces choices, how opportunity cost measures those '
                   'choices, and how a production possibility curve models an economy\'s options.',
        'days': [
            {
                'title': 'Needs, wants and scarcity',
                'minutes': 45,
                'objectives': [
                    'Learners will define Economics.',
                    'Learners will distinguish between needs and wants, and between goods and services.',
                    'Learners will explain the economic problem of scarcity and choice.',
                ],
                'notes': (
                    '<p><strong>Economics</strong> is the study of how people, businesses and governments '
                    '<strong>use scarce resources</strong> to satisfy their <strong>unlimited wants</strong>.</p>'
                    '<ul>'
                    '<li><strong>Needs</strong> are things we must have to survive: food, water, shelter, clothing.</li>'
                    '<li><strong>Wants</strong> are things we would like to have: a smartphone, a car, holidays. '
                    'Human wants are <strong>unlimited</strong> — once one is satisfied, another appears.</li>'
                    '<li><strong>Goods</strong> are tangible (you can touch them, e.g. bread); <strong>services</strong> '
                    'are intangible (e.g. a haircut, teaching).</li>'
                    '<li><strong>Free goods</strong> (e.g. air, sunlight) are unlimited and have no price; '
                    '<strong>economic goods</strong> are scarce and have a price.</li>'
                    '</ul>'
                    '<p>The resources used to make goods and services — <strong>natural resources, labour, '
                    'capital and entrepreneurship</strong> — are <strong>scarce</strong> (limited).</p>'
                    '<p>This creates the <strong>basic economic problem</strong>: <em>unlimited wants but limited '
                    'resources</em>. Because of <strong>scarcity</strong>, every individual, business and '
                    'government must make <strong>choices</strong>. Scarcity is not the same as poverty: even '
                    'rich countries face scarcity, because they cannot produce everything their people want.</p>'
                ),
                'key_terms': [
                    ('Economics', 'The study of how scarce resources are used to satisfy unlimited wants.'),
                    ('Scarcity', 'The situation in which resources are limited relative to wants.'),
                    ('Economic goods', 'Goods that are scarce and therefore have a price.'),
                    ('Free goods', 'Goods available in unlimited quantities at no cost, e.g. air.'),
                ],
                'example': {
                    'title': 'Class activity: needs vs wants',
                    'html': (
                        '<p>Sort these items into <strong>needs</strong> and <strong>wants</strong>:</p>'
                        '<p>bread, designer sneakers, a school uniform, clean water, a gaming console, '
                        'a blanket, take-away pizza, medicine, data bundles.</p>'
                        '<ul>'
                        '<li><strong>Needs:</strong> bread, a school uniform (clothing), clean water, a blanket, medicine.</li>'
                        '<li><strong>Wants:</strong> designer sneakers, a gaming console, take-away pizza.</li>'
                        '<li><strong>Discuss:</strong> data bundles — a need for online learning, or a want? The '
                        'answer depends on context, which shows that needs and wants can change over time.</li>'
                        '</ul>'
                    ),
                },
                'video': {'id': 's07CZN48spE', 'title': 'Grade 10 Economics: Basic Concepts and The Economic Problem | Study Squad', 'channel': 'Kleva Academy', 'minutes': 10},
                'worksheet': {
                    'instructions': 'Answer the questions on the economic problem.',
                    'exercises': [
                        '1. Define Economics.',
                        '2. Distinguish between needs and wants, with TWO examples of each.',
                        '3. Distinguish between goods and services.',
                        '4. Explain the difference between free goods and economic goods.',
                        '5. What is the basic economic problem?',
                        '6. Explain why rich countries also face scarcity.',
                    ],
                },
                'quiz': [
                    ('mcq', 'The basic economic problem is ...',
                     ['unlimited resources and limited wants', 'unlimited wants and limited resources',
                      'too much money', 'too many goods'], 1),
                    ('tf', 'Air is an example of a free good.', True),
                    ('mcq', 'Which is a service?', ['A loaf of bread', 'A haircut', 'A school bag', 'A bicycle'], 1),
                    ('mcq', 'Scarcity means that ...',
                     ['resources are limited relative to wants', 'goods are free', 'people have no needs', 'prices are always low'], 0),
                ],
                'homework': {
                    'title': 'My wants list',
                    'instructions': 'Think about your household.',
                    'tasks': [
                        'List five needs and five wants of your household.',
                        'Explain in 5–6 lines how scarcity forces your household to make choices.',
                    ],
                    'marks': 10,
                },
            },
            {
                'title': 'Choice, opportunity cost and the basic economic questions',
                'minutes': 45,
                'objectives': [
                    'Learners will define and calculate opportunity cost.',
                    'Learners will explain the three basic economic questions.',
                    'Learners will apply opportunity cost to choices made by individuals, businesses and government.',
                ],
                'notes': (
                    '<p>Because resources are scarce, choosing one option means giving up another. The '
                    '<strong>opportunity cost</strong> is the value of the <strong>next best alternative '
                    'forgone</strong> (given up) when a choice is made.</p>'
                    '<ul>'
                    '<li><strong>Individual:</strong> if you spend Saturday studying instead of working at a shop '
                    'for R300, the opportunity cost of studying is the R300 you could have earned.</li>'
                    '<li><strong>Business:</strong> a farmer who plants maize on a field cannot plant sunflowers '
                    'on it; the sunflower crop is the opportunity cost.</li>'
                    '<li><strong>Government:</strong> money spent on a new stadium cannot be spent on clinics.</li>'
                    '</ul>'
                    '<p>Every economy must answer <strong>three basic economic questions</strong>:</p>'
                    '<ol>'
                    '<li><strong>What</strong> to produce, and how much?</li>'
                    '<li><strong>How</strong> to produce (which combination of resources and technology)?</li>'
                    '<li><strong>For whom</strong> to produce (how output is distributed)?</li>'
                    '</ol>'
                    '<p>Different <em>economic systems</em> answer these questions differently: in a market '
                    'economy prices and consumers decide; in a centrally planned economy the government decides; '
                    'most countries, including South Africa, have a <strong>mixed economy</strong>.</p>'
                ),
                'key_terms': [
                    ('Opportunity cost', 'The value of the next best alternative given up when making a choice.'),
                    ('Choice', 'Deciding how to use scarce resources among alternatives.'),
                    ('Mixed economy', 'An economy in which both the market and the government decide what, how and for whom to produce.'),
                ],
                'example': {
                    'title': 'Worked example: calculating opportunity cost',
                    'html': (
                        '<p>Nomsa has R500. Her options, in order of preference: (1) a pair of jeans, (2) a concert '
                        'ticket, (3) saving the money.</p>'
                        '<p>She buys the jeans. The opportunity cost is the <strong>concert ticket</strong> — her next '
                        'best alternative — <em>not</em> the ticket and the savings together.</p>'
                        '<p><strong>Production example:</strong> A factory can make either 400 chairs or 100 tables '
                        'with the same resources in a week.</p>'
                        '<ul>'
                        '<li>Opportunity cost of 1 table = 400 ÷ 100 = <strong>4 chairs</strong>.</li>'
                        '<li>Opportunity cost of 1 chair = 100 ÷ 400 = <strong>0.25 tables</strong>.</li>'
                        '</ul>'
                    ),
                },
                'video': {'id': 'fSo777le8qo', 'title': 'Scarcity and Opportunity Cost | Economics Explained', 'channel': 'Federal Reserve Bank of St. Louis', 'minutes': 5},
                'worksheet': {
                    'instructions': 'Answer the questions. Show calculations.',
                    'exercises': [
                        '1. Define opportunity cost.',
                        '2. Thabo can work a shift for R250 or go to a soccer match. He chooses the match. What is the opportunity cost?',
                        '3. A bakery can bake 600 loaves or 200 cakes per day. Calculate the opportunity cost of 1 cake.',
                        '4. Name and explain the three basic economic questions.',
                        '5. Give an example of opportunity cost for the South African government.',
                        '6. Explain how a mixed economy answers the question "for whom to produce?".',
                    ],
                },
                'quiz': [
                    ('mcq', 'Opportunity cost is the ...',
                     ['next best alternative forgone', 'price of a good', 'total of all alternatives', 'cost of production'], 0),
                    ('mcq', 'A farm can produce 300 bags of maize or 150 bags of beans. The opportunity cost of 1 bag of beans is ...',
                     ['0.5 bags of maize', '2 bags of maize', '150 bags of maize', '3 bags of maize'], 1),
                    ('tf', 'The three basic economic questions are what, how and for whom to produce.', True),
                    ('mcq', 'South Africa has a ... economy.', ['pure market', 'centrally planned', 'mixed', 'traditional only'], 2),
                ],
                'homework': {
                    'title': 'Opportunity cost in my life',
                    'instructions': 'Reflect and calculate.',
                    'tasks': [
                        'Describe three choices you made this week and the opportunity cost of each.',
                        'A tailor can make 20 shirts or 8 suits per week. Calculate the opportunity cost of one suit and of one shirt.',
                    ],
                    'marks': 10,
                },
            },
            {
                'title': 'Production possibility curves',
                'minutes': 50,
                'objectives': [
                    'Learners will draw a production possibility curve (PPC) from a table.',
                    'Learners will interpret points on, inside and outside the curve.',
                    'Learners will explain increasing opportunity cost and shifts of the PPC.',
                ],
                'notes': (
                    '<p>A <strong>production possibility curve (PPC)</strong> shows the <strong>maximum '
                    'combinations</strong> of two goods an economy can produce when it uses <em>all</em> its '
                    'resources efficiently, with given technology.</p>'
                    '<ul>'
                    '<li><strong>Points on the curve</strong> — efficient production (full employment of resources).</li>'
                    '<li><strong>Points inside the curve</strong> — inefficient; resources are unemployed or '
                    'under-used (e.g. during a recession or load shedding).</li>'
                    '<li><strong>Points outside the curve</strong> — unattainable with current resources and technology.</li>'
                    '</ul>'
                    '<p>Moving along the curve shows <strong>opportunity cost</strong>: to make more of one good, '
                    'the economy must give up some of the other. The PPC is usually <strong>concave</strong> '
                    '(bowed outward) because of <strong>increasing opportunity cost</strong> — resources are not '
                    'equally suited to producing both goods.</p>'
                    '<p>The PPC <strong>shifts outward</strong> (economic growth) when the quantity or quality of '
                    'resources increases or technology improves — e.g. more skilled workers, new machinery. It '
                    'shifts <strong>inward</strong> if resources are destroyed, e.g. by war or natural disasters.</p>'
                ),
                'key_terms': [
                    ('PPC', 'Production possibility curve: shows maximum output combinations of two goods.'),
                    ('Efficiency', 'Using all resources fully so that output cannot be increased without giving something up.'),
                    ('Increasing opportunity cost', 'Each extra unit of one good requires giving up more and more of the other.'),
                    ('Economic growth', 'An increase in productive capacity, shown by an outward shift of the PPC.'),
                ],
                'example': {
                    'title': 'Worked example: food and machines',
                    'html': (
                        '<p>A country\'s production possibilities:</p>'
                        '<ul>'
                        '<li>A: 0 machines, 100 units food</li>'
                        '<li>B: 10 machines, 90 food</li>'
                        '<li>C: 20 machines, 70 food</li>'
                        '<li>D: 30 machines, 40 food</li>'
                        '<li>E: 40 machines, 0 food</li>'
                        '</ul>'
                        '<ol>'
                        '<li>A to B: 10 more machines cost 10 food = <strong>1 food per machine</strong>.</li>'
                        '<li>B to C: 10 more machines cost 20 food = <strong>2 food per machine</strong>.</li>'
                        '<li>C to D: 10 more machines cost 30 food = <strong>3 food per machine</strong>.</li>'
                        '<li>D to E: 10 more machines cost 40 food = <strong>4 food per machine</strong>.</li>'
                        '</ol>'
                        '<p>The opportunity cost <strong>increases</strong>, so the PPC is concave. The combination '
                        '20 machines and 50 food lies <strong>inside</strong> the curve (inefficient); 30 machines and '
                        '60 food lies <strong>outside</strong> it (unattainable).</p>'
                    ),
                },
                'video': {'id': 'O6XL__2CDPU', 'title': 'Production Possibilities Curve Review', 'channel': 'Jacob Clifford', 'minutes': 6},
                'worksheet': {
                    'instructions': 'Use graph paper. Show all calculations.',
                    'exercises': [
                        '1. Plot the PPC from the class example (machines on the x-axis, food on the y-axis).',
                        '2. Mark a point that shows inefficient production and explain why.',
                        '3. Mark a point that is unattainable and explain why.',
                        '4. Calculate the opportunity cost of moving from point C to point D.',
                        '5. Explain why the PPC is concave (bowed outward).',
                        '6. Draw a new PPC to show the effect of new technology. What does the shift represent?',
                        '7. Give TWO events that would shift the South African PPC inward.',
                    ],
                },
                'quiz': [
                    ('mcq', 'A point inside the PPC shows ...',
                     ['efficient production', 'unemployed or under-used resources', 'unattainable output', 'economic growth'], 1),
                    ('mcq', 'An outward shift of the PPC represents ...',
                     ['a recession', 'war damage', 'inflation', 'economic growth'], 3),
                    ('tf', 'A PPC is usually concave because of increasing opportunity cost.', True),
                    ('mcq', 'Using the class table, the opportunity cost of moving from B to C is ...',
                     ['10 units of food', '20 units of food', '30 units of food', '70 units of food'], 1),
                ],
                'homework': {
                    'title': 'Draw and interpret a PPC',
                    'instructions': 'Use the table: computers / maize (tonnes): A 0/50, B 5/45, C 10/35, D 15/20, E 20/0.',
                    'tasks': [
                        'Draw the PPC on graph paper with labelled axes.',
                        'Calculate the opportunity cost of each move (A to B, B to C, C to D, D to E).',
                        'Explain what happens to opportunity cost as more computers are produced.',
                    ],
                    'marks': 15,
                },
            },
        ],
    },
    (11, 'ECON'): {
        'topic': 'Factors of production',
        'caps': 'Economics Grade 11, Term 1, Macroeconomics — Factors of production: natural resources '
                '(land), labour, capital and entrepreneurship; their characteristics, remuneration, '
                'productivity and interaction',
        'summary': 'Learners examine the four factors of production, how each is rewarded, and how '
                   'their quality, quantity and productivity determine an economy\'s output.',
        'days': [
            {
                'title': 'Introduction and natural resources',
                'minutes': 50,
                'objectives': [
                    'Learners will name the four factors of production and their rewards.',
                    'Learners will explain the characteristics of natural resources.',
                    'Learners will distinguish between renewable and non-renewable resources and discuss sustainability.',
                ],
                'notes': (
                    '<p><strong>Factors of production</strong> are the resources used to produce goods and '
                    'services. Each factor earns a <strong>reward (remuneration)</strong>:</p>'
                    '<ul>'
                    '<li><strong>Natural resources (land)</strong> — earn <strong>rent</strong></li>'
                    '<li><strong>Labour</strong> — earns <strong>wages and salaries</strong></li>'
                    '<li><strong>Capital</strong> — earns <strong>interest</strong></li>'
                    '<li><strong>Entrepreneurship</strong> — earns <strong>profit</strong></li>'
                    '</ul>'
                    '<p>Land, labour and capital are combined by the entrepreneur.</p>'
                    '<p><strong>Natural resources</strong> are all gifts of nature: land, minerals (gold, '
                    'platinum, coal), water, forests, fish, the climate. Characteristics:</p>'
                    '<ul>'
                    '<li>The <strong>supply is fixed</strong> (limited) — we cannot make more land.</li>'
                    '<li>They are <strong>immobile</strong> geographically (you cannot move a gold reef).</li>'
                    '<li>They are <strong>heterogeneous</strong> — they differ in quality and location.</li>'
                    '<li>They are subject to the <strong>law of diminishing returns</strong>.</li>'
                    '</ul>'
                    '<p><strong>Renewable</strong> resources (sun, wind, forests if replanted) can be replaced; '
                    '<strong>non-renewable</strong> resources (coal, oil, gold) are used up. South Africa relies '
                    'heavily on mining and coal, so <strong>sustainable use</strong> — meeting today\'s needs '
                    'without harming future generations — is a major economic issue.</p>'
                ),
                'key_terms': [
                    ('Factors of production', 'The resources used to produce goods and services: natural resources, labour, capital, entrepreneurship.'),
                    ('Remuneration', 'The reward earned by a factor of production.'),
                    ('Rent', 'The reward for the use of natural resources.'),
                    ('Sustainability', 'Using resources so that future generations can also meet their needs.'),
                ],
                'example': {
                    'title': 'Guided activity: factors in a bakery',
                    'html': (
                        '<p>Identify the factor of production and its reward:</p>'
                        '<ul>'
                        '<li>The plot where the bakery stands — <strong>natural resources</strong>; reward: <strong>rent</strong>.</li>'
                        '<li>The bakers and cashiers — <strong>labour</strong>; reward: <strong>wages</strong>.</li>'
                        '<li>Ovens, mixers and the delivery van — <strong>capital</strong>; reward: <strong>interest</strong>.</li>'
                        '<li>Mrs Dlamini, who started the business and takes the risk — <strong>entrepreneurship</strong>; '
                        'reward: <strong>profit</strong>.</li>'
                        '</ul>'
                        '<p><em>Note:</em> Flour is a raw material made from natural resources (wheat, soil, water) '
                        'and labour; it is an intermediate good, not a separate factor.</p>'
                    ),
                },
                'video': {'id': '8Xg9rRmskHg', 'title': 'Factors of Production | Economics Explained', 'channel': 'Federal Reserve Bank of St. Louis', 'minutes': 5},
                'worksheet': {
                    'instructions': 'Answer the questions on factors of production and natural resources.',
                    'exercises': [
                        '1. Name the four factors of production and the reward each earns.',
                        '2. Give FOUR examples of natural resources found in South Africa.',
                        '3. Explain THREE characteristics of natural resources.',
                        '4. Distinguish between renewable and non-renewable resources.',
                        '5. Explain why the sustainable use of coal is important for South Africa.',
                        '6. Identify the factors of production in a taxi business.',
                    ],
                },
                'quiz': [
                    ('mcq', 'The reward for entrepreneurship is ...', ['rent', 'wages', 'interest', 'profit'], 3),
                    ('mcq', 'Which is a non-renewable resource?', ['Wind', 'Sunlight', 'Coal', 'Forests that are replanted'], 2),
                    ('tf', 'The supply of natural resources is fixed.', True),
                    ('mcq', 'The reward for the use of natural resources is ...', ['rent', 'profit', 'salaries', 'dividends'], 0),
                ],
                'homework': {
                    'title': 'Natural resources of South Africa',
                    'instructions': 'Research and write.',
                    'tasks': [
                        'Name three natural resources South Africa exports and one province where each is found.',
                        'Explain one way each resource can be used more sustainably.',
                    ],
                    'marks': 12,
                },
            },
            {
                'title': 'Labour and capital',
                'minutes': 50,
                'objectives': [
                    'Learners will explain the quantity and quality of labour.',
                    'Learners will calculate labour productivity.',
                    'Learners will distinguish between types of capital and explain capital formation.',
                ],
                'notes': (
                    '<p><strong>Labour</strong> is human effort, physical and mental, used in production. Its '
                    'contribution depends on:</p>'
                    '<ul>'
                    '<li><strong>Quantity:</strong> the size of the labour force, which depends on population size, '
                    'age structure, participation rate and working hours.</li>'
                    '<li><strong>Quality:</strong> education, training, skills, health and motivation. Investment in '
                    'people is called <strong>human capital</strong>.</li>'
                    '</ul>'
                    '<p><strong>Productivity</strong> measures output per unit of input. '
                    '<strong>Labour productivity = total output ÷ number of workers (or hours worked)</strong>. '
                    'Higher productivity allows higher wages without raising prices.</p>'
                    '<p><strong>Capital</strong> is man-made goods used to produce other goods and services.</p>'
                    '<ul>'
                    '<li><strong>Fixed capital:</strong> durable assets used repeatedly, e.g. machines, buildings, '
                    'vehicles.</li>'
                    '<li><strong>Circulating (working) capital:</strong> items used up in one production cycle, e.g. '
                    'raw materials, fuel.</li>'
                    '<li><strong>Social capital (infrastructure):</strong> roads, ports, power stations, schools.</li>'
                    '</ul>'
                    '<p><strong>Capital formation</strong> is the increase in the stock of capital. It requires '
                    '<strong>saving</strong> (giving up consumption today) and <strong>investment</strong>. '
                    '<strong>Depreciation</strong> is the wear and tear of capital that must be replaced.</p>'
                ),
                'key_terms': [
                    ('Labour productivity', 'Output per worker or per hour worked.'),
                    ('Human capital', 'The skills, knowledge and health of workers.'),
                    ('Fixed capital', 'Durable capital goods used repeatedly in production.'),
                    ('Capital formation', 'An increase in the stock of capital through saving and investment.'),
                ],
                'example': {
                    'title': 'Worked example: labour productivity',
                    'html': (
                        '<p><strong>Factory A:</strong> 10 workers produce 2 000 loaves per day.<br>'
                        'Labour productivity = 2 000 ÷ 10 = <strong>200 loaves per worker per day</strong>.</p>'
                        '<p><strong>Factory B:</strong> 8 workers with a new mixer produce 2 400 loaves per day.<br>'
                        'Labour productivity = 2 400 ÷ 8 = <strong>300 loaves per worker per day</strong>.</p>'
                        '<p>Increase from A to B = (300 − 200) ÷ 200 × 100 = <strong>50%</strong>.</p>'
                        '<p><em>Explain:</em> Factory B is more productive because each worker has more '
                        '<strong>capital</strong> (the mixer) to work with. This shows how the factors of production '
                        'work together.</p>'
                    ),
                },
                'video': {'id': 'NGOXqXxUoDc', 'title': 'Gr11 Economics | Factors of production | Term 1', 'channel': 'SANELANE', 'minutes': 15},
                'worksheet': {
                    'instructions': 'Answer the questions. Show calculations.',
                    'exercises': [
                        '1. Explain FOUR factors that determine the quantity of labour.',
                        '2. Explain how education and health improve the quality of labour.',
                        '3. 25 workers assemble 1 500 cellphones in a day. Calculate labour productivity.',
                        '4. After training, the same 25 workers assemble 1 800 cellphones. Calculate the percentage increase in productivity.',
                        '5. Distinguish between fixed and circulating capital, with examples.',
                        '6. Why is saving necessary for capital formation?',
                    ],
                },
                'quiz': [
                    ('mcq', '12 workers produce 600 shirts per day. Labour productivity is ...',
                     ['50 shirts per worker', '72 shirts per worker', '600 shirts per worker', '12 shirts per worker'], 0),
                    ('mcq', 'Raw materials used up in production are ... capital.',
                     ['fixed', 'social', 'circulating', 'human'], 2),
                    ('tf', 'Roads and power stations are examples of social capital (infrastructure).', True),
                    ('mcq', 'The reward for capital is ...',
                     ['rent', 'wages', 'profit', 'interest'], 3),
                ],
                'homework': {
                    'title': 'Productivity and capital',
                    'instructions': 'Show all workings.',
                    'tasks': [
                        'A farm employs 20 workers who harvest 4 000 kg of oranges per day. After buying a new machine, 16 workers harvest 4 800 kg. Calculate productivity before and after, and the percentage change.',
                        'Explain two reasons why South Africa\'s labour productivity is lower than that of some other countries.',
                    ],
                    'marks': 15,
                },
            },
            {
                'title': 'Entrepreneurship and the interaction of the factors',
                'minutes': 50,
                'objectives': [
                    'Learners will explain the role and characteristics of the entrepreneur.',
                    'Learners will explain how the factors of production interact to produce output.',
                    'Learners will discuss the importance of entrepreneurship for the South African economy.',
                ],
                'notes': (
                    '<p>The <strong>entrepreneur</strong> is the person who <strong>combines</strong> natural '
                    'resources, labour and capital to produce goods and services, and who '
                    '<strong>bears the risk</strong> of the business. The reward is <strong>profit</strong> — '
                    'or a loss if the venture fails.</p>'
                    '<p><strong>Functions of the entrepreneur:</strong></p>'
                    '<ul>'
                    '<li>Identifies a <strong>business opportunity</strong> (a need in the market).</li>'
                    '<li><strong>Organises</strong> the other factors of production in the most efficient way.</li>'
                    '<li><strong>Takes risks</strong> and makes decisions under uncertainty.</li>'
                    '<li><strong>Innovates</strong> — introduces new products, methods or markets.</li>'
                    '</ul>'
                    '<p><strong>Characteristics:</strong> creativity, initiative, perseverance, willingness to take '
                    'calculated risks, leadership and good management skills.</p>'
                    '<p><strong>Interaction:</strong> no factor can produce on its own. Output depends on the '
                    '<em>combination</em> of factors; for example, a mine needs a mineral deposit (natural '
                    'resources), miners and engineers (labour), drilling machines (capital) and a mining company '
                    '(entrepreneurship).</p>'
                    '<p>In South Africa, with high <strong>unemployment</strong>, entrepreneurs and small businesses '
                    '(SMMEs) are important for creating jobs, innovation and economic growth.</p>'
                ),
                'key_terms': [
                    ('Entrepreneur', 'A person who combines the factors of production, takes risks and seeks profit.'),
                    ('Innovation', 'Introducing new products, processes or ways of doing things.'),
                    ('SMME', 'Small, medium and micro enterprise.'),
                    ('Risk', 'The possibility of losing money invested in a business.'),
                ],
                'example': {
                    'title': 'Case study: Lindiwe\'s solar business',
                    'html': (
                        '<p><em>During load shedding, Lindiwe noticed that families in her township needed affordable '
                        'backup power. She rented a small workshop, borrowed R60 000 from a bank to buy tools and '
                        'stock, and hired two electricians to install small solar kits.</em></p>'
                        '<ul>'
                        '<li><strong>Opportunity identified:</strong> demand for affordable backup power.</li>'
                        '<li><strong>Natural resources:</strong> the workshop site (rent) and sunlight (a free, renewable resource).</li>'
                        '<li><strong>Labour:</strong> two electricians (wages).</li>'
                        '<li><strong>Capital:</strong> tools and stock financed by a loan (interest).</li>'
                        '<li><strong>Entrepreneurship:</strong> Lindiwe organises the factors and takes the risk (profit).</li>'
                        '</ul>'
                        '<p>If her monthly sales are R85 000 and her total costs (rent, wages, interest, stock and '
                        'other costs) are R71 000, her <strong>profit</strong> = 85 000 − 71 000 = <strong>R14 000</strong>.</p>'
                    ),
                },
                'video': {'id': 'RSyvcANRaOE', 'title': 'The Four Factors of Production', 'channel': 'Professor Dave Explains', 'minutes': 5},
                'worksheet': {
                    'instructions': 'Answer the questions on entrepreneurship.',
                    'exercises': [
                        '1. Define an entrepreneur.',
                        '2. Explain FOUR functions of the entrepreneur.',
                        '3. List FIVE characteristics of a successful entrepreneur.',
                        '4. Use the Lindiwe case study to identify each factor of production and its reward.',
                        '5. Explain why entrepreneurship is important for reducing unemployment in South Africa.',
                        '6. Explain why an entrepreneur may earn a loss instead of a profit.',
                    ],
                },
                'quiz': [
                    ('mcq', 'Who combines the other factors of production and bears the risk?',
                     ['The landowner', 'The worker', 'The entrepreneur', 'The bank'], 2),
                    ('tf', 'An entrepreneur is always guaranteed a profit.', False),
                    ('mcq', 'Sales R50 000 and total costs R42 000 give a profit of ...', ['R92 000', 'R8 000', 'R42 000', 'R50 000'], 1),
                    ('mcq', 'Introducing a new product or method is called ...',
                     ['innovation', 'depreciation', 'remuneration', 'capital formation'], 0),
                ],
                'homework': {
                    'title': 'Business idea',
                    'instructions': 'Plan a small business you could start in your community.',
                    'tasks': [
                        'Describe the opportunity you have identified.',
                        'Explain how you would use each of the four factors of production and what each would earn.',
                        'Identify two risks you would face.',
                    ],
                    'marks': 15,
                },
            },
        ],
    },
    (12, 'ECON'): {
        'topic': 'Macroeconomics: the circular flow',
        'caps': 'Economics Grade 12, Term 1, Macroeconomics — Circular flow: the open economy model '
                '(participants, markets, real and money flows), leakages and injections, national account '
                'aggregates and the multiplier',
        'summary': 'Learners build the circular flow model of an open economy, analyse leakages and '
                   'injections, convert between national account aggregates and calculate the multiplier.',
        'days': [
            {
                'title': 'The open economy circular flow: participants, markets and flows',
                'minutes': 50,
                'objectives': [
                    'Learners will name the four participants and three markets in the circular flow.',
                    'Learners will distinguish between real flows and money flows.',
                    'Learners will draw and explain the circular flow of an open economy.',
                ],
                'notes': (
                    '<p>The <strong>circular flow model</strong> shows how goods, services, factors of production '
                    'and money move between the participants in an economy. An <strong>open economy</strong> trades '
                    'with the rest of the world.</p>'
                    '<p><strong>Participants:</strong></p>'
                    '<ul>'
                    '<li><strong>Households</strong> — own the factors of production; buy goods and services (consumption, C).</li>'
                    '<li><strong>Firms</strong> — buy factors of production and produce goods and services; invest (I).</li>'
                    '<li><strong>Government (public sector)</strong> — collects taxes (T) and spends (G).</li>'
                    '<li><strong>Foreign sector</strong> — buys our exports (X) and sells us imports (M).</li>'
                    '</ul>'
                    '<p><strong>Markets:</strong></p>'
                    '<ul>'
                    '<li><strong>Goods (product) market</strong> — final goods and services are traded.</li>'
                    '<li><strong>Factor market</strong> — factors of production are traded for rent, wages, interest and profit.</li>'
                    '<li><strong>Financial market</strong> — savings are channelled to borrowers for investment.</li>'
                    '</ul>'
                    '<p><strong>Flows:</strong> <em>Real flows</em> are the movement of goods, services and factors '
                    'of production. <em>Money flows</em> (in the opposite direction) are the payments for them: '
                    'income, spending, taxes and so on.</p>'
                    '<p>Total spending in an open economy: <strong>Y = C + I + G + (X − M)</strong>.</p>'
                ),
                'key_terms': [
                    ('Open economy', 'An economy that trades with other countries.'),
                    ('Real flow', 'The flow of goods, services and factors of production.'),
                    ('Money flow', 'The flow of payments for goods, services and factors.'),
                    ('Factor market', 'The market where factors of production are bought and sold.'),
                ],
                'example': {
                    'title': 'Guided drawing: the four-sector model',
                    'html': (
                        '<ol>'
                        '<li>Draw <strong>Households</strong> on the left and <strong>Firms</strong> on the right; '
                        'the <strong>goods market</strong> at the top and the <strong>factor market</strong> at the bottom.</li>'
                        '<li>Real flow: households supply <em>factors</em> to the factor market; firms supply '
                        '<em>goods and services</em> to the goods market.</li>'
                        '<li>Money flow: firms pay <em>rent, wages, interest and profit</em> to households; households '
                        'pay <em>consumption spending (C)</em> to firms.</li>'
                        '<li>Add <strong>Government</strong> in the centre: taxes (T) in, government spending (G) out.</li>'
                        '<li>Add the <strong>Foreign sector</strong>: exports (X) money in, imports (M) money out.</li>'
                        '<li>Add the <strong>financial market</strong>: savings (S) in, investment (I) out.</li>'
                        '</ol>'
                    ),
                },
                'video': {'id': 'f15__0izZGY', 'title': 'Lesson 1 Circular Flow of an Open Economy TDBS Economics Grade 12 by Carden Madzokere #economics', 'channel': 'Carden Madzokere', 'minutes': 10},
                'worksheet': {
                    'instructions': 'Answer the questions on the circular flow.',
                    'exercises': [
                        '1. Name the four participants in an open economy.',
                        '2. Name the three markets and explain what is traded in each.',
                        '3. Distinguish between real flows and money flows, with an example of each.',
                        '4. What do households receive in exchange for supplying labour?',
                        '5. Write the equation for total spending in an open economy and explain each symbol.',
                        '6. Draw a fully labelled circular flow diagram of an open economy.',
                    ],
                },
                'quiz': [
                    ('mcq', 'Which participant is added to make an open economy?', ['Households', 'Firms', 'The foreign sector', 'The government'], 2),
                    ('mcq', 'In which market are factors of production traded?',
                     ['Goods market', 'Financial market', 'Factor market', 'Foreign market'], 2),
                    ('tf', 'Money flows move in the opposite direction to real flows.', True),
                    ('mcq', 'In Y = C + I + G + (X − M), "M" stands for ...', ['money', 'imports', 'markets', 'multiplier'], 1),
                ],
                'homework': {
                    'title': 'Circular flow diagram',
                    'instructions': 'Draw on an A4 page.',
                    'tasks': [
                        'Draw a fully labelled circular flow diagram of an open economy showing real and money flows in different colours.',
                        'Explain the role of the financial market in 4–6 lines.',
                    ],
                    'marks': 12,
                },
            },
            {
                'title': 'Leakages, injections and equilibrium',
                'minutes': 50,
                'objectives': [
                    'Learners will identify the leakages and injections in the circular flow.',
                    'Learners will explain the condition for equilibrium in an open economy.',
                    'Learners will predict the effect of changes in leakages and injections on national income.',
                ],
                'notes': (
                    '<p><strong>Leakages (withdrawals)</strong> are income that leaves the circular flow and is '
                    'not spent on domestic goods:</p>'
                    '<ul>'
                    '<li><strong>Savings (S)</strong> by households</li>'
                    '<li><strong>Taxes (T)</strong> paid to government</li>'
                    '<li><strong>Imports (M)</strong> — spending on foreign goods</li>'
                    '</ul>'
                    '<p><strong>Injections</strong> are spending that enters the flow from outside the household–firm loop:</p>'
                    '<ul>'
                    '<li><strong>Investment (I)</strong> by firms</li>'
                    '<li><strong>Government spending (G)</strong></li>'
                    '<li><strong>Exports (X)</strong> — foreign spending on our goods</li>'
                    '</ul>'
                    '<p><strong>Equilibrium</strong> occurs when <strong>total leakages = total injections</strong>: '
                    '<strong>S + T + M = I + G + X</strong>. Then national income is stable.</p>'
                    '<ul>'
                    '<li>If <strong>injections &gt; leakages</strong>, spending rises and national income '
                    '<strong>increases</strong> (expansion).</li>'
                    '<li>If <strong>leakages &gt; injections</strong>, spending falls and national income '
                    '<strong>decreases</strong> (contraction).</li>'
                    '</ul>'
                    '<p>Government uses this idea in <em>fiscal policy</em>: in a recession it may increase G or cut '
                    'T to stimulate the economy.</p>'
                ),
                'key_terms': [
                    ('Leakage', 'Income withdrawn from the circular flow: savings, taxes, imports.'),
                    ('Injection', 'Spending added to the circular flow: investment, government spending, exports.'),
                    ('Equilibrium', 'The state in which leakages equal injections and national income is stable.'),
                ],
                'example': {
                    'title': 'Worked example: is the economy in equilibrium?',
                    'html': (
                        '<p>Figures in R billion: S = 300, T = 1 500, M = 1 400; I = 450, G = 1 700, X = 1 300.</p>'
                        '<ol>'
                        '<li>Leakages = 300 + 1 500 + 1 400 = <strong>R3 200 bn</strong>.</li>'
                        '<li>Injections = 450 + 1 700 + 1 300 = <strong>R3 450 bn</strong>.</li>'
                        '<li>Injections exceed leakages by <strong>R250 bn</strong>.</li>'
                        '<li>Conclusion: the economy is <strong>not</strong> in equilibrium; national income will '
                        '<strong>increase</strong> until leakages rise to equal injections.</li>'
                        '</ol>'
                    ),
                },
                'video': {'id': 'LAsgrt1DH-s', 'title': 'Lesson 3 Leakages and Injections TDBS Economics Grade 12 by Carden Madzokere #circularflowofincome', 'channel': 'Carden Madzokere', 'minutes': 10},
                'worksheet': {
                    'instructions': 'Answer the questions. Show calculations.',
                    'exercises': [
                        '1. Name the three leakages and the three injections.',
                        '2. Write the equilibrium condition for an open economy.',
                        '3. S = 200, T = 900, M = 800, I = 350, G = 1 000, X = 650 (R bn). Is the economy in equilibrium? What will happen to national income?',
                        '4. Explain how an increase in imports affects the circular flow.',
                        '5. Explain how government can use G and T to stimulate a weak economy.',
                        '6. Why is saving a leakage but also linked to investment?',
                    ],
                },
                'quiz': [
                    ('mcq', 'Which is a leakage?', ['Exports', 'Investment', 'Savings', 'Government spending'], 2),
                    ('mcq', 'Which is an injection?', ['Taxes', 'Imports', 'Savings', 'Exports'], 3),
                    ('tf', 'If injections are greater than leakages, national income will increase.', True),
                    ('mcq', 'The equilibrium condition in an open economy is ...',
                     ['S + T + M = I + G + X', 'S + I = T + G', 'C + I = G + X', 'S = M'], 0),
                ],
                'homework': {
                    'title': 'Leakages and injections',
                    'instructions': 'Answer with calculations and explanations.',
                    'tasks': [
                        'S = 280, T = 1 200, M = 1 150, I = 400, G = 1 250, X = 900 (R bn). Calculate total leakages and injections and state what will happen to national income.',
                        'Explain two ways a fall in world demand for South African minerals would affect the circular flow.',
                    ],
                    'marks': 12,
                },
            },
            {
                'title': 'National account aggregates and the multiplier',
                'minutes': 55,
                'objectives': [
                    'Learners will explain the three methods of measuring GDP.',
                    'Learners will convert GDP at market prices to basic prices and factor cost, and calculate GNI.',
                    'Learners will calculate and explain the multiplier.',
                ],
                'notes': (
                    '<p><strong>Gross Domestic Product (GDP)</strong> is the total value of all final goods and '
                    'services produced <em>within the borders</em> of a country in a period (usually a year). It '
                    'can be measured in three ways that should give the same answer:</p>'
                    '<ul>'
                    '<li><strong>Production method</strong> — total value added by all sectors.</li>'
                    '<li><strong>Income method</strong> — total income earned by the factors of production.</li>'
                    '<li><strong>Expenditure method</strong> — total spending: C + I + G + (X − M).</li>'
                    '</ul>'
                    '<p><strong>Conversions:</strong></p>'
                    '<ul>'
                    '<li>GDP at market prices − taxes on products + subsidies on products = <strong>GDP at basic prices</strong></li>'
                    '<li>GDP at basic prices − other taxes on production + other subsidies on production = '
                    '<strong>GDP at factor cost</strong></li>'
                    '<li>GDP + primary income from the rest of the world − primary income to the rest of the world = '
                    '<strong>Gross National Income (GNI)</strong></li>'
                    '</ul>'
                    '<p><strong>The multiplier</strong>: an increase in an injection causes a <em>larger</em> final '
                    'increase in national income, because one person\'s spending becomes another person\'s income. '
                    'k = 1 ÷ (1 − mpc), or in an open economy <strong>k = 1 ÷ (mps + mpt + mpm)</strong>, where '
                    'mpc is the marginal propensity to consume.</p>'
                ),
                'key_terms': [
                    ('GDP', 'The value of all final goods and services produced within a country in a year.'),
                    ('GNI', 'Income earned by a country\'s permanent residents, at home and abroad.'),
                    ('Basic prices', 'Market prices minus taxes on products plus subsidies on products.'),
                    ('Multiplier', 'The number of times a change in injections changes national income.'),
                ],
                'example': {
                    'title': 'Worked example: conversions and the multiplier',
                    'html': (
                        '<p><strong>(a) Conversions</strong> (R billion): GDP at market prices 6 000; taxes on products '
                        '550; subsidies on products 30; other taxes on production 60; other subsidies on production 20.</p>'
                        '<ol>'
                        '<li>GDP at basic prices = 6 000 − 550 + 30 = <strong>5 480</strong></li>'
                        '<li>GDP at factor cost = 5 480 − 60 + 20 = <strong>5 440</strong></li>'
                        '</ol>'
                        '<p>If primary income from the rest of the world is 120 and to the rest of the world is 270: '
                        'GNI (market prices) = 6 000 + 120 − 270 = <strong>5 850</strong>.</p>'
                        '<p><strong>(b) Multiplier:</strong> mpc = 0.8, so k = 1 ÷ (1 − 0.8) = 1 ÷ 0.2 = <strong>5</strong>. '
                        'A R10 bn increase in government spending raises national income by 10 × 5 = <strong>R50 bn</strong>.</p>'
                    ),
                },
                'video': {'id': 'smARMus5Qdk', 'title': 'How To MASTER The MULTIPLIER Effect in Economics | Grade 12 | 2025', 'channel': 'Masterclass With The General', 'minutes': 15},
                'worksheet': {
                    'instructions': 'Answer the questions. Show all calculations.',
                    'exercises': [
                        '1. Define GDP and name the three methods of measuring it.',
                        '2. GDP at market prices R5 200 bn; taxes on products R480 bn; subsidies on products R25 bn. Calculate GDP at basic prices.',
                        '3. Use your answer to Q2: other taxes on production R50 bn; other subsidies on production R15 bn. Calculate GDP at factor cost.',
                        '4. Explain the difference between GDP and GNI.',
                        '5. mpc = 0.75. Calculate the multiplier.',
                        '6. Using Q5, by how much will national income increase if investment rises by R8 bn?',
                        '7. Explain why a higher mpc leads to a larger multiplier.',
                    ],
                },
                'quiz': [
                    ('mcq', 'GDP at market prices − taxes on products + subsidies on products = ...',
                     ['GDP at factor cost', 'Net exports', 'GNI', 'GDP at basic prices'], 3),
                    ('mcq', 'If mpc = 0.9, the multiplier is ...', ['0.9', '1.1', '9', '10'], 3),
                    ('tf', 'GDP measures production within the borders of a country.', True),
                    ('mcq', 'With a multiplier of 4, an injection of R5 bn increases national income by ...',
                     ['R1.25 bn', 'R9 bn', 'R20 bn', 'R5 bn'], 2),
                ],
                'homework': {
                    'title': 'National accounts and multiplier practice',
                    'instructions': 'Show all workings.',
                    'tasks': [
                        'GDP at market prices R7 100 bn; taxes on products R620 bn; subsidies on products R40 bn; other taxes on production R70 bn; other subsidies on production R25 bn. Calculate GDP at basic prices and at factor cost.',
                        'mps = 0.15, mpt = 0.2, mpm = 0.15. Calculate the open-economy multiplier and the change in income if exports rise by R12 bn.',
                        'Explain, using the multiplier, why government spending on infrastructure can boost the whole economy.',
                    ],
                    'marks': 20,
                },
            },
        ],
    },
}
