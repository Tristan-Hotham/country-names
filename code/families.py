"""Name families for the countries whose many names have a well-documented history.

Each family has: a short label, what the name comes from (only as far as the cited article says), a regular expression
tried against the romanised name (lower case, from anyascii), the source article and a quote from it that the build
checks word for word. Families are tried in order; a name that matches none is 'other'.
"""
F = {}

F["Q183"] = dict(article="Names of Germany", fams=[
    ("diutisc", "Deutsch family", "from Old High German diutisc, 'of the people'",
     r"deut|duits|duut|d[uü]tsch|dutsl|daitsch|deitsch|doich|doitsu|dogil|^duc$|duiska|tysk|thysk|tjiisk|deguo|daik-guok|tek-kok|tet-koet|theod|ubudage|doych|dyyt|dwzgoz|^idai|^de$",
     'the German language endonym is Deutschland, from the Old High German diutisc, meaning "of the people"'),
    ("nemets", "Niemcy family", "from Slavic němьci, 'the mutes' or 'the speechless'",
     r"miemie|niem|nemc|nemeck|nemet|nemsk|nims|nimet|nimech|njema|nemach|nyamech|nemych|mjymcy|nemshin|nemec",
     "in Polish it is Niemcy, from the Proto-Slavic *němьcь, meaning speechless, since German is not mutually intelligible with Slavic languages"),
    ("saxon", "Saksa family", "from the Saxon tribe", r"saks|saxo",
     "in Finnish it is Saksa, from the name of the Saxon tribe"),
    ("baltic", "Vokietija family", "Baltic, origin unclear, perhaps 'those who shout'", r"vokiet|vacija|vuokit|vaacija",
     "in Lithuanian it is Vokietija, of unclear origin"),
    ("germania", "Germany family", "from the Latin Germania", r"germ|gierm|gjerm|girm|jerm|jarm|jrm|jamus|jamin|jamen|jemani|jerem|jarim|gyaam|grmn|jr-m|cerum|zerman|kelem|siama|tiama|heremani|dzherm|ghearm|ghermaan|jalimani|jalimane|girimane|gyamn|miunkyamni|yormni|djerm|jarumanu|joermani|eygnlaman|jarmalka|jerum",
     "in Italian it is Germania, from the Latin Germania"),
    ("alemanni", "Allemagne family", "from the Alamanni tribe", r"alem|allem|alam|alim|alman|almay|almag|almn|lalman|lmny|almaen|almaanya|elmny|alleum|olmon",
     "the French exonym is Allemagne, from the name of the Alamanni tribe"),
])

F["Q148"] = dict(article="List of country-name etymologies", fams=[
    ("zhongguo", "Zhongguo family", "Zhongguo, 'Middle Kingdom' or 'Central Nation', read in each language",
     r"zhong|chung|jung|trung|tiong|dung-hua|krung|cunghvaz|^chu-?goku|^chugoku",
     'the most common endonym: originally meaning "Central Demesne", then "Middle Kingdom", now equivalent to "Central Nation"'),
    ("cathay", "Kitai family", "Cathay, from the Khitan people", r"kita|kytay|qitay|qytay|kitdin|khitad|khyatad|hytay|xitoy|kitai|khyt|^khitay|k'ytay|kh'utey",
     'Cathay, a former & literary name: "Khitai", from Marco Polo\'s Italian Catai'),
    ("china", "China family", "China, usually traced to the Qin state", r"chin|cin|kina|kiin|sina|^sin|tsin|txin|chyn|shin|siin|chen|cain|caen|chain|chaay|hiina|ccinwa|haina|seen|tshaena|tjhaena|tzina|xina|saina|siaina|chayna|cayina|chyin|tsiene|tsii|shiina|ubushinwa|ishayina|caina|chine|khyn|lsyn|tsiy|tsie|ch-ina|sine|cheen|syn|ch'in|kinij|chunwa|sjiin|shyn|ciin|kine|kenej",
     'Often said that the word "China" and its related terms are derived from the Qin state'),
])

F["Q41"] = dict(article="Names of Greece", fams=[
    ("hellas", "Hellas family", "from Hellas, the Greeks' own name", r"ell|hell|helen|^hela|xila|hy lap|hi-liap|hi-le-na|sihla|yelen",
     "Hellás, the local endonym"),
    ("yunan", "Yunan family", "from the Ionians, via Old Persian Yauna", r"yuna|yunon|yewn|yown|hown|yoon|yvvn|ywn|yonn|lywnn|lyunan|ywenn|yvnd|aunn|buyonaani|^yvn|yonan",
     "It was derived from the Old Persian Yauna for the Ionian Greeks"),
    ("graeci", "Greece family", "from the Latin Graecus, the Graikoi", r"gre|gri|grc|grk|grec|gres|krek|kreik|kree|grt|grj|ghre|kalis|kulit|giri|geres|geuli|kiri|^kre|krech|recko|grek|igrik|ngirik|gerika|gelesi|gorog|graek|graik|ke-ri|kris|kres|greek|krak|krit|crec|grts|grez|griach|gyres|griis|girees|giris|ugirik|gryk|kire|g'r|groeg|grae|ubugere",
     "From Old English Grecas and Crecas, from Latin Græcus, presumably from Greek Graikoí"),
], source_override={"hellas": "List of country-name etymologies", "graeci": "List of country-name etymologies"})

F["Q55"] = dict(article="Names of the Netherlands", fams=[
    ("low", "'Low countries' translated", "a translation of 'low countries'", r"bas|bass|bajo|baix|baxo|baxu|bascio|vasci|de jos|alankomaat|vuollee|herbehere|iseldir|isiltir|tirean isle|izelvro|urasuyu|timura n wadda|alamad|vualadahen|vue'll|echkapan|peyiba",
     "many languages have the same word for both the country of the Netherlands and the region of the Low Countries, e.g., French (les Pays-Bas), Spanish (los Países Bajos) and Portuguese (Países Baixos)"),
    ("holland", "Holland family", "from the province of Holland, 'wooded land'", r"hol|olan|ollan|oranda|helan|ho-lan|hlnd|hulanda|hvlnd|hwlnd|horana|ha lan|h'l'nd|hu'lnd|kholand|hollnga|olaand|hwzlanz|ohnlang|holane|holani|gwlln|ho-ln",
     'Holland, a former name: From the region of Holland within the Netherlands, often used by metonymy for the country as a whole'),
    ("belanda", "Belanda", "the Malay and Indonesian name (my sources do not trace its origin)", r"belanda|walanda", "Hindia-Belanda, a former name: the Indonesian form of the Dutch name above"),
    ("nederland", "Nederland family", "Nederland, 'low land', borrowed by sound", r"ned|neth|nid|nyd|neer|nizoz|netal|nethi|nekelan|niid|nedd|nied|neez|nit|ne-dr|nydar|nethrl|netrl|nysal|need",
     "Netherlands literally means Low countries or Lowlands"),
], source_override={"holland": "List of country-name etymologies", "nederland": "List of country-name etymologies", "belanda": "List of country-name etymologies"})

F["Q28"] = dict(article="List of country-name etymologies", fams=[
    ("magyar", "Magyar family", "from Magyar, the Hungarians' own name", r"mad'|magy|mady|madj|madz|madar|macar|majar|majori|mazhar|mojar|mezhar|mecar|mjr|lmjr|m'jri|madzh|magar",
     'Magyarország (native name - "land of the Magyars")'),
    ("ugry", "Węgry family", "from Turkic on-ogur, 'ten arrows', Slavic forms", r"wegry|vengr|wengr|ugorsh|vugorsh|vengria|vengraye|vengreje",
     'Turkic: on-ogur, "(people of the) ten arrows"'),
    ("hungary", "Hungary family", "from Turkic on-ogur, 'ten arrows', with a nod to the Huns", r"hun|hon|ung|ong|hng|ank|hang|heong|hamg|hmg|hvng|xiong|hiung|unkar|unriya|yungh|hengr|hanek|unggar|'vng|hwng|oygg|howng|hnng|hvni|haneg",
     "The ethnonym Hunni (referring to the Huns) has influenced the Latin (and English) spelling"),
])

F["Q33"] = dict(article="Names of Finland", fams=[
    ("suomi", "Suomi family", "Suomi, the Finns' own name (origin uncertain)", r"suom|soom|somij|suop|suhom",
     "Suomi, used in Finnish and, in corresponding forms, in the other Finnic languages"),
    ("finland", "Finland family", "Old Norse, 'land of the Finns'", r"fin|fen|phin|pin|fyn|fn ?l|hpin|hun-lan|hung-lang|feel|phan lan|fuin|flnd|pynl|ffind|winil|hiland|hineran|ifini|ufini|pineti|fnlnd|fanl|fhion|fun-lan|ph'in|phnl|fiinl|efnglang",
     "Finland, a name of Old Norse origin used in Swedish and, in various forms, in most other languages"),
])

F["Q17"] = dict(article="Names of Japan", fams=[
    ("nihon", "Nihon family", "日本 'sun origin', read in each language", r"nihon|nippon|nipon|nihun|riben|ilbon|nhat ban|jit-pun|ngit-pun|nik-buong|nibun|nditbonj|^ri-pin|yipun|^nixuudin|nipoun",
     "The Japanese names for Japan are Nihon"),
    ("japan", "Japan family", "Japan, via Marco Polo and Malay from a Chinese reading of 日本", r"jap|giap|jepang|jepun|yapon|yapan|iapon|iapan|xapon|zhapon|zhpon|zhpn|zhpu|zhpwn|zhapan|chapon|chapaan|chap'on|chbon|chpn|hapon|hapun|hapo|jpan|jpn|jppan|jpwn|ljpwn|lybn|sapong|siapan|djap|gappun|giappo|giapp|giapun|iapani|ijaphani|ubuyapani|zapo|jipun|djapon|yfn|y'f'n|ypwna|gypnn|kyapon|zipun|jabaan|seapain|d'oppuon|j-apon|j-pn|tsaquan|xaapon|jopon|jaap|iap'",
     "The word Japan is an exonym, and is used (in one form or another) by many languages"),
])

F["Q79"] = dict(article="List of country-name etymologies", fams=[
    ("misr", "Misr family", "Misr, the ancient Semitic name", r"misr|misir|masr|masar|mesir|mesire|msr|msyr|mysr|mysyr|musur|mis'ru|misyr|misra|misri|mtsrym|maser|masat|misar",
     "The current name of Egypt, Misr/Misir/Misru, stems from the Ancient Semitic name for it"),
    ("egypt", "Egypt family", "from Greek Aigyptos, 'home of the ka of Ptah'", r"gyp|gip|gyf|gipt|egit|egyp|ejip|ejyp|eijp|ijip|ijib|idjip|isip|exip|ezit|ehip|ihip|ekip|echip|edji|egep|ejit|eigit|ai cap|aiji|ai-gik|ai-khip|ai-kip|ayifto|aikup|aehciz|igibh|aifft|eipheit|eigipt|gbts|i-ci|i-jib|itsiq|iqip|iegip|egvip|egiip|ikip|igyc|ehseib|eyib|oiyipt|'ikyip|edjipe|eg-ipte|egjip|egyip|eggitt|ijiip|ejiip",
     '"Home of the ka of Ptah", from Latin Aegyptus, from Greek Aígyptos'),
])

F["Q230"] = dict(article="List of country-name etymologies", fams=[
    ("sakartvelo", "Sakartvelo family", "Sakartvelo, 'place for Kartvelians'", r"sakart|sakort|kartvel|kartul|qyrth",
     'Sakartvelo, the local endonym: "Place for Kartvelians" in Georgian'),
    ("gurj", "Gurjistan and Gruzia family", "from Persian Gurğ, the source of 'Georgia' too", r"gurj|gurc|gurz|gruz|gruu|groz|grez|grjstn|grjstw|gwrj|gyrc|gyurdzh|guyrdzy|gorjist|jwrj|jurj|gvrgyh|grvzy|gu'rzh|pow grouzi|jorjia|jrjy|jrjia|jarj|jorj|jyorj|joorj|jojia|jiyojia|jiyorj|ciyarc|qiaozhi|gelujiya|seosia|siaosia|keokia|horia|georg|giorg|gjeorg|geolg|xeorx|zeorz|cheorch|djiordj|djordj|jeorj|jeoj|jeoor|ji'oor|joaj|juoja|tsaatsii|chorshey|tseoirsia|chorech|kyeakya|gyeagyi|jau-j|'jor-ji|chchchei|ijojiya|geworugiya|jarjiya|xkxi|jrjiy|jorg|g'vrg",
     'Georgia" seems to have been borrowed in the 11th or 12th century from the Syriac Gurz-ān or -iyān and Arabic Ĵurĵan or Ĵurzan, derived from the New Persian Gurğ or Gurğān'),
])

F["Q222"] = dict(article="List of country-name etymologies", fams=[
    ("shqip", "Shqipëria family", "Shqipëri, 'land of the understanding'", r"shqip|shkip",
     'Shqipëri, its modern endonym: "Land of the Understanding", from the Albanian adverb shqip, "understanding each other"'),
    ("arnavut", "Arnavutluk family", "Ottoman Turkish, from Byzantine Greek Arbanitai", r"arnav|arnaw|arnaut|arngud|arnauy",
     'Arnavutluk, its Ottoman Turkish name: "Land of the Albanians", a metathesis from Byzantine Greek Arbanitai'),
    ("albania", "Albania family", "'land of the Albanians', from Byzantine Greek Albania", r"alb|alv|alp|lbn|lvn|aerban|alib|alab|alub|alwan|avana|arapein|arbain|arumb|arub|elban|elbn|lbny|l-b-ni|l-p-ny|apaniya|anbani|aolebeni|alqueni|aliqueni|aelbeniy|ylbheni|'lv'ny|'lbny|albeen|al'ban|aeoleben|alepan|alipan",
     '"Land of the Albanians", Latinized from Byzantine Greek Albanía'),
])

F["Q399"] = dict(article="List of country-name etymologies", fams=[
    ("hayastan", "Hayastan family", "Hayastan, from Hayk", r"hayast|^hay",
     "The modern Armenian Hayastan () derives from earlier Armenian Hayk"),
    ("armenia", "Armenia family", "'land of the Armenioi', from Old Persian Armina", r"arm|erm|rmn|rmy|amen|amin|ameni|alem|alim|aamiin|aarman|rm'n|'rm|r-me|yamein|ormeny|virmen|aleumen|arume|jermen|kemni|armeeni|'amen|arim|airm",
     'Latinized from Greek Armenía (Ἀρμενία), "Land of the Armenioi"'),
])

F["Q159"] = dict(article="List of country-name etymologies", fams=[
    ("venaja", "Venäjä family", "after the ancient Venedes", r"ven[aä]|venama|venemaa|ven'a", "Vene or Venemaa (Estonian) and Venäjä (Finnish): after the ancient Venedes"),
    ("krievija", "Krievija", "after the ancient Krivichs", r"krievij", "Krievija, named after the ancient Krivichs tribe"),
    ("rus", "Rus family", "from the Rus', named after Roslagen in Sweden", r"rus|ros|ras|rws|rrus|rus|ruos|russ|roosh|rois|rach|rash|rsi|rsy|rsiy|ris|luss|lusia|leosia|lo-se|eluosi|ruhia|ruis|riis|ratsiy|rooseev|ruush|rwa|orosz|oros|urus|urys|rurh|arass|irash|uburus|uruc|rvs|ezlozs|r-shi|rtsya|roshia|rasha|resey|rassey|orsin|rochmu|ladex|rasesiy|u-ru-su|ryss|rwws|rrows|roush|ruus|roos",
     "Generally agreed to be from a Varangian group known as the Rus', named after the Roslagen region in Sweden"),
])

F["Q34"] = dict(article="List of country-name etymologies", fams=[
    ("ruotsi", "Ruotsi family", "after the Roslagen region, 'rowers'", r"ruots|rootsi|ruott|ruota|ruocc",
     "Rootsi (Estonian) and Ruotsi (Finnish): named after the Roslagen region in Sweden"),
    ("svea", "Sweden family", "from the Swedes; Sverige is 'Swedish realm'", r"sw|sv|sue|szw|shv|isv|isw|suw|soe|soi|sui|suv|suy|siw|si-we|svi|zvez|zwe|schwe|cuvit|chvid|chuid|thuy dien|kueken|huiten|lswyd|swyd|syed|sswid|sued|swid|soy|zviedr|suec|suesi|svec|svez|sves|sveko|svezia|shved|showet|shuet|svoriki|sweoland|toolynn|nyeiqdenj|xoued|swiedn|su'i|suu|widen|iswe|iswi|isvet|sbezz|sual|suain|seuwed",
     '"Swedes", an old English plural form of Swede'),
])

F["Q38"] = dict(article="List of country-name etymologies", fams=[
    ("walh", "Włochy and Olaszország", "from Gothic walh, 'foreigner', the root of Wales and Wallachia",
     r"wlochy|olasz", "Włochy (Polish) and Olaszország (Hungarian): from Gothic walh, the same root as in Valland and Wallachia"),
    ("italia", "Italy family", "from Latin Italia, from an early people of southern Italy", r".", "From Latin Ītalia, itself from Greek Ἰταλία"),
])
