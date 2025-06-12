"""Language detection module for name analysis."""

from __future__ import annotations

import re
from functools import lru_cache

from .core import Language


# German language patterns
GERMAN_PATTERNS = [
    r"ß|ä|ö|ü",  # German umlauts and eszett
    r"\b(von|van|der|zu|zur|am|im)\b",  # German particles
    r"(bach|berg|burg|feld|hausen|heim|mann|stein)$",  # German surname endings
    r"\b(hans|friedrich|wolfgang|günther|heinrich|klaus|ludwig|kurt|otto|fritz)\b",  # German names
]

# French language patterns
FRENCH_PATTERNS = [
    r"ç|è|é|ê|à|ù|û|î|ô|ë|ï|ÿ",  # French accents
    r"\b(du|des|le|la|les|d')\b",  # French particles (removed "de" to avoid Spanish confusion)
    r"(eau|eux|ieux|tion|sion)$",  # French endings
    r"\b(jean|pierre|françois|michel|andré|jacques|henri|philippe|patrice|claude|bernard|alain|christian|christophe|olivier|nicolas|laurent|thierry|pascal|frédéric|sébastien|antoine|emmanuel|vincent|stéphane|dominique|julien|bruno|eric|fabrice|didier|gérard|rené|roger|yves|maurice|marcel|louis|francis|lucien|albert|raymond|gabriel|gilbert|paul|andre|denis|gerard|joseph|simon|xavier|edouard|georges|charles)\b",  # French male names (removed ambiguous ones)
    r"\b(françoise|monique|sylvie|isabelle|catherine|christine|brigitte|martine|véronique|nicole|nathalie|chantal|danielle|jacqueline|michèle|annie|joséphine|marguerite|jeanne|denise|simone|madeleine|suzanne|andrée|louise|marcelle|hélène|georgette|yvette|germaine|thérèse|bernadette|paulette|solange|ginette|colette|odette|huguette|pierrette|arlette|gisèle|josette|lucette|marceline|henriette|antoinette|elisabeth|elise|claire|sylvie|anne|anna)\b",  # French female names (removed ambiguous ones)
    r"(pierre|claire|luc|paul|andré|rené)$",  # Common French name endings (removed "josé" which is more Spanish)
    r"-",  # French compound names often use hyphens
]

# Italian language patterns
ITALIAN_PATTERNS = [
    r"[àèéìíîòóùú]",  # Italian accents
    r"\b(di|del|della|dei|delle|dello|degli|da|dal|dalla|dallo|dalle|san|santa|santo)\b",  # Italian particles
    r"(acci|elli|etti|ini|ino|ina|etto|etta|ucci|uzzi)$",  # Italian diminutive endings
    r"\b(alessandro|andrea|antonio|carlo|francesco|giovanni|giuseppe|lorenzo|luca|marco|matteo|michele|paolo|roberto|stefano|alberto|angelo|bruno|claudio|daniele|davide|emanuele|enrico|fabio|federico|filippo|franco|gabriele|giacomo|giorgio|giulio|leonardo|luigi|mario|massimo|maurizio|nicola|pietro|riccardo|salvatore|sergio|simone|tommaso|umberto|vincenzo)\b",  # Italian male names
    r"\b(alessandra|anna|antonella|barbara|carla|caterina|chiara|cristina|daniela|elena|elisabetta|federica|francesca|giovanna|giulia|giuseppina|laura|lucia|luisa|manuela|margherita|maria|marina|marta|michela|monica|paola|patrizia|raffaella|rita|roberta|rosa|rosanna|sara|serena|silvia|simona|stefania|teresa|valentina|valeria)\b",  # Italian female names
    r"\b(rossi|russo|ferrari|esposito|bianchi|romano|colombo|ricci|marino|greco|bruno|gallo|conti|de luca|costa|giordano|mancini|rizzo|lombardi|moretti|barbieri|fontana|santoro|mariani|rinaldi|caruso|ferrara|galli|martini|leone|longo|gentile|martinelli|vitale|lombardo|serra|coppola|de santis|d'angelo|marchetti|parisi|villa|conte|ferretti|pellegrini|palumbo|sanna|fabbri|montanari|grassi|giuliani|benedetti|barone|rossetti|caputo|montanaro|guerra|palmieri|bernardi|martino|fiore|de angelis|mazza|silvestri|testa|grassi|pellegrino|carbone|giuliano|benedetto|donati|ruggiero|orlando|damico|ferri|galli|cattaneo|bianco|valentini|pagano|sorrentino|basile|santini|ferraro|galli|farina|rizzi|morelli|amato|milani|esposito|cattaneo|de rosa|bruno|galli|ferrari|russo|bianchi|romano|ricci|marino|greco|gallo|conti|costa|giordano|mancini|rizzo|lombardi|moretti)\b",  # Italian surnames
]

# Spanish language patterns
SPANISH_PATTERNS = [
    r"[áéíóúüñ]",  # Spanish accents and ñ
    r"\b(de|del|de la|de las|de los|y|e|san|santa|santo|da|das|dos|do)\b",  # Spanish particles
    r"(ez|az|iz|oz|uz)$",  # Spanish patronymic endings
    r"\b(alejandro|antonio|carlos|daniel|david|francisco|javier|jesús|josé|juan|luis|manuel|miguel|pablo|pedro|rafael|ramón|ricardo|roberto|sergio|vicente|adrián|alberto|alfonso|andrés|ángel|arturo|diego|eduardo|emilio|enrique|fernando|guillermo|ignacio|jaime|jorge|leonardo|lorenzo|marcos|mario|martín|nicolás|oscar|raúl|rubén|salvador|santiago|tomás|víctor)\b",  # Spanish male names
    r"\b(maría|ana|carmen|josefa|isabel|dolores|pilar|teresa|rosa|francisca|antonia|mercedes|esperanza|ángeles|concepción|manuela|elena|cristina|patricia|laura|marta|beatriz|silvia|mónica|andrea|lucía|raquel|sara|natalia|alejandra|paula|eva|rocío|julia|esther|irene|nuria|susana|yolanda|amparo|gloria|inmaculada|montserrat|remedios|encarnación|rosario|consuelo|soledad|asunción|milagros|nieves|aurora|blanca|estrella|lourdes|marisol|noelia|paloma|rocío|sonia|verónica)\b",  # Spanish female names
    r"\b(garcía|rodríguez|gonzález|fernández|lópez|martínez|sánchez|pérez|gómez|martín|jiménez|ruiz|hernández|díaz|moreno|álvarez|muñoz|romero|alonso|gutiérrez|navarro|torres|domínguez|vázquez|ramos|gil|ramírez|serrano|blanco|suárez|molina|morales|ortega|delgado|castro|ortiz|rubio|marín|sanz|iglesias|medina|garrido|cortés|castillo|santos|lozano|guerrero|cano|prieto|méndez|cruz|herrera|peña|flores|cabrera|campos|vega|fuentes|carrasco|diez|caballero|reyes|nieto|aguilar|pascual|herrero|montero|lorenzo|hidalgo|giménez|ibáñez|ferrer|duran|santiago|benítez|mora|vicente|vargas|arias|carmona|crespo|román|pastor|soto|sáez|velasco|moya|soler|parra|esteban|bravo|gallego|rojas|estévez|vidal|molina|león|peña|mendoza|guerrero|medina|cortés|contreras|jiménez|herrera|guzmán|vargas|castillo|ramírez|torres|flores|rivera|gómez|díaz|cruz|morales|reyes|gutiérrez|ortiz|chávez|ramos|herrera|méndez|ruiz|álvarez|vásquez|castillo|moreno|romero|herrera|medina|guerrero|cruz|ortega|gómez|vargas|gonzález|pérez|sánchez|ramírez|torres|rivera|flores|gómez|díaz|reyes|morales|cruz|ortiz|gutiérrez|chávez|ramos|álvarez|vásquez|castillo|moreno|romero|herrera|medina|guerrero|ortega|vargas|gonzález|pérez|sánchez|ramírez|torres|rivera|flores)\b",  # Spanish surnames
]

# Portuguese language patterns
PORTUGUESE_PATTERNS = [
    r"[ãõ]",  # Portuguese-specific tildes (more distinctive than other accents)
    r"\b(dos|são|joão|antónio|antônio|gonçalo|goncalo|conceição|conceicao)\b",  # Very Portuguese-specific words
    r"(ção|ssão|inho|inha|ões)$",  # Portuguese endings
    r"\b(joão|josé|antónio|antônio|francisco|manuel|rui|hugo|tiago|sérgio|sergio|nuno|gonçalo|goncalo|diogo|bernardo|rodrigo|filipe|felipe|guilherme|renato|márcio|marcio|fábio|fabio|júlio|julio|césar|cesar|adriano|cristiano|leandro|flávio|flavio|caio|mateus|luciano|thiago)\b",  # Distinctly Portuguese male names
    r"\b(catarina|joana|teresa|tereza|francisca|luísa|luisa|beatriz|inês|inez|patricia|rita|vera|sílvia|silvia|fernanda|raquel|mónica|monica|susana|cláudia|claudia|célia|celia|fátima|fatima|helena|manuela|conceição|conceicao|lurdes|glória|gloria|graça|graca|eduarda|bárbara|barbara|margarida|marlene|filipa|olívia|olivia|lúcia|lucia|rute|vitória|victoria|leonor|bruna|sónia|sonia|vanessa|carolina|daniela|andreia|andréia|liliana|anabela|tânia|tania)\b",  # Distinctly Portuguese female names
    r"\b(silva|santos|ferreira|pereira|oliveira|costa|rodrigues|martins|jesus|sousa|fernandes|gonçalves|gomes|lopes|marques|alves|almeida|ribeiro|pinto|carvalho|teixeira|moreira|correia|mendes|nunes|soares|vieira|monteiro|cardoso|rocha|neves|coelho|cunha|pires|reis|antunes|machado|miranda|castro|lima|henriques|dias|caetano|fonseca|morais|magalhães|valente|pacheco|esteves|tavares|barros|carneiro|guedes|freitas|barbosa|faria|sá|brito|leite|melo)\b",  # Portuguese surnames
]

# Chinese/Mandarin language patterns
CHINESE_PATTERNS = [
    r"[\u4e00-\u9fff\u3400-\u4dbf]",  # Chinese characters (simplified and traditional)
    r"\b(wang|li|zhang|liu|chen|yang|huang|zhao|zhou|wu|xu|sun|zhu|ma|hu|guo|lin|he|gao|liang|zheng|luo|song|xie|tang|han|cao|deng|xiao|feng|zeng|cheng|cai|peng|pan|yuan|yu|dong|su|ye|wei|jiang|tian|du|ding|shen|fan|fu|zhong|lu|dai|cui|ren|liao|yao|fang|jin|qiu|xia|tan|zou|shi|xiong|meng|qin|yan|xue|hou|lei|bai|long|duan|hao|kong|shao|mao|chang|wan|gu|lai|wu|kang|he|yan|yin|qian|niu|hong|gong)\b",  # Common Chinese surnames (romanized)
    r"\b(wong|lee|chang|lau|chan|yeung|chiu|chow|ng|tsui|soon|chu|mah|woo|kwok|lam|ho|ko|leung|cheng|law|sung|tse|tong|hon|tso|hui|siu|fung|tsang|ching|choy|pang|poon|yuen|tung|so|yip|lui|wai|cheung|tin|to|ting|sum|keung|fan|kong|foo|chung|lou|toy|chui|yam|luk|liu|yiu|fong|kam|yau|har|tam|kar|chau|sek|hung|mang|chun|yim|sit|hau|pak|lung|tuen|see|mou|sheung|man|koo|loi|mo|hor|wan|chin|ngau|kung)\b",  # Hong Kong/Cantonese romanizations
    r"\b(wei|ming|hua|jian|jun|lei|tao|chao|bin|hui|gang|peng|fei|kai|jie|liang|long|zhi|hai|dong|yang|chun|hao|tian|wen|wu|kang|jian|hong|bo|li|hong|xia|yan|juan|fang|mei|ling|jing|min|ping|lan|ying|xue|lin|ying|jie|xiu|hua|yue|ning|yu|ting|jing|xin|qian|na|yao|lei|wei|zhen|qin|yun|feng|lu|jia)\b",  # Common Chinese given names (romanized)
]

# Arabic language patterns
ARABIC_PATTERNS = [
    r"[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]",  # Arabic script
    r"\b(al|el|ibn|bin|bint|abu|um|abd)\b",  # Arabic particles (romanized)
    r"\b(muhammad|mohamed|mohammed|mohammad|ahmad|ahmed|ali|abdullah|abdallah|omar|umar|yusuf|yousef|ibrahim|hassan|hussein|khalid|khaled|salem|salim|mansour|mahmoud|amr|saeed|said|nasser|waleed|walid|osama|tariq|faisal|adel|rami|samer|karim|hakim|marwan|mazen|majed|nabil|wael|ziad|riad|adnan|jamal|maged|hatim|hazem|tamer|bassam)\b",  # Arabic male names
    r"\b(fatima|fatma|aisha|aysha|khadija|mariam|maryam|zainab|zaynab|safiya|hafsa|ruqayya|asma|salma|nour|noor|rana|rania|dina|hala|layla|laila|hanan|mona|muna|reem|rim|noha|ghada|sawsan|widad|siham|nawal|amina|samira|karima|wafa|maha|suad|najwa|thuraya|farah|dalia|yasmin|yasmeen|leena|lina|tala|lara|maya|sara|sarah|jana)\b",  # Arabic female names
    r"(allah|rahman|aziz|malik|hassan|hussein)$",  # Common Arabic name endings
]

# Russian language patterns
RUSSIAN_PATTERNS = [
    r"[\u0400-\u04FF\u0500-\u052F\u2DE0-\u2DFF\uA640-\uA69F]",  # Cyrillic script
    r"\b(де|ван|фон|ла|ле|дю)\b",  # Russian particles (Cyrillic)
    r"\b(de|van|von|la|le|du)\b",  # Russian particles (romanized)
    r"(ович|евич|ич|овна|евна|ична)$",  # Russian patronymic endings (Cyrillic)
    r"(ovich|evich|ich|ovna|evna|ichna)$",  # Russian patronymic endings (romanized)
    r"\b(александр|алексей|андрей|антон|артем|борис|владимир|дмитрий|евгений|игорь|иван|константин|максим|михаил|николай|олег|павел|петр|роман|сергей|анна|елена|ирина|мария|наталья|ольга|светлана|татьяна|юлия|екатерина)\b",  # Russian names (Cyrillic)
    r"\b(aleksandr|aleksey|andrey|anton|artem|boris|vladimir|dmitriy|evgeniy|igor|ivan|konstantin|maksim|mikhail|nikolay|oleg|pavel|petr|roman|sergey|anna|elena|irina|mariya|natalya|olga|svetlana|tatyana|yuliya|ekaterina|alexander|alexey|andrew|anthony|arthur|michael|nicholas|peter|sergei|natasha|katya|sasha|misha|dima|vova|kolya|pasha|roma|max|maxim)\b",  # Russian names (romanized)
    r"\b(иванов|петров|сидоров|смирнов|кузнецов|попов|лебедев|козлов|новиков|морозов|петров|волков|соловьев|васильев|зайцев|павлов|семенов|голубев|виноградов|богданов|воробьев|федоров|михайлов|беляев|тарасов|белов|комаров|орлов|киселев|макаров|андреев|ковалев|ильин|гусев|титов|кузьмин|кудрявцев|баранов|куликов|алексеев|степанов|яковлев|сорокин|сергеев|романов|захаров|борисов|королев|герасимов|пономарев|григорьев|лазарев|медведев|ершов|никитин|соболев|рябов|поляков|цветков|данилов|жуков|фролов|журавлев|николаев|крылов|максимов|сидоров|осипов|белоусов|федотов|дорофеев|егоров|матвеев|бобров|дмитриев|калинин|анисимов|петухов|антонов|тимофеев|никифоров|веселов|филиппов|марков|большаков|суханов|миронов|ширяев|александров|коновалов|шестаков|казаков|ефимов|денисов|громов|фомин|давыдов|мельников|щербаков|блинов|колесников|карпов|афанасьев|власов|маслов|исаков|тихонов|аксенов|гаврилов|родионов|котов|горбунов|кудряшов|быков|зуев|третьяков|савельев|панов|рыбаков|суворов|абрамов|воронов|мухин|архипов|трофимов|мартынов|емельянов|горшков|чернов|овчинников|селезнев|панфилов|копылов|михеев|галкин|назаров|лобанов|лукин|беляков|потапов|некрасов|хохлов|жданов|наумов|шилов|воронцов|ермаков|дроздов|игнатьев|савин|логинов|сафонов|капустин|кириллов|моисеев|елисеев|кошелев|костин|горбачев|орехов|ефремов|исаев|евдокимов|калашников|кабанов|носков|юдин|кулагин|лапин|прохоров|нестеров|харитонов|агафонов|муравьев|ларионов|матюшин|дементьев|гуляев|борисенко|прокофьев|биryков|шаров|мясников|лыткин|большов|краснов|рыжов|сычев|батурин|стрелков|пестов|русаков|стариков|щукин|барабанов|зимин|молчанов|глухов|симонов|землянов|бирюков|кольцов|шульгин|князев|лаврентьев|устинов|грибов|вишняков|сазонов|богомолов|золотарев)\b",  # Russian surnames (Cyrillic)
    r"\b(ivanov|petrov|sidorov|smirnov|kuznetsov|popov|lebedev|kozlov|novikov|morozov|volkov|solovyov|vasiliev|zaitsev|pavlov|semenov|golubev|vinogradov|bogdanov|vorobyov|fedorov|mikhailov|belyaev|tarasov|belov|komarov|orlov|kiselev|makarov|andreev|kovalev|ilyin|gusev|titov|kuzmin|kudryavtsev|baranov|kulikov|alekseev|stepanov|yakovlev|sorokin|sergeev|romanov|zakharov|borisov|korolev|gerasimov|ponomarev|grigoriev|lazarev|medvedev|ershov|nikitin|sobolev|ryabov|polyakov|tsvetkov|danilov|zhukov|frolov|zhuravlev|nikolaev|krylov|maksimov|osipov|belousov|fedotov|dorofeev|egorov|matveev|bobrov|dmitriev|kalinin|anisimov|petukhov|antonov|timofeev|nikiforov|veselov|filippov|markov|bolshakov|sukhanov|mironov|shiryaev|aleksandrov|konovalov|shestakov|kazakov|efimov|denisov|gromov|fomin|davydov|melnikov|shcherbakov|blinov|kolesnikov|karpov|afanasiev|vlasov|maslov|isakov|tikhonov|aksenov|gavrilov|rodionov|kotov|gorbunov|kudryashov|bykov|zuev|tretyakov|saveliev|panov|rybakov|suvorov|abramov|voronov|mukhin|arkhipov|trofimov|martynov|emelyanov|gorshkov|chernov|ovchinnikov|seleznev|panfilov|kopylov|mikheev|galkin|nazarov|lobanov|lukin|belyakov|potapov|nekrasov|khokhlov|zhdanov|naumov|shilov|vorontsov|ermakov|drozdov|ignatiev|savin|loginov|safonov|kapustin|kirillov|moiseev|eliseev|koshelev|kostin|gorbachev|orekhov|efremov|isaev|evdokimov|kalashnikov|kabanov|noskov|yudin|kulagin|lapin|prokhorov|nesterov|kharitonov|agafonov|muraviev|larionov|matyushin|dementiev|gulyaev|borisenko|prokofiev|biryukov|sharov|myasnikov|lytkin|bolshov|krasnov|ryzhov|sychev|baturin|strelkov|pestov|rusakov|starikov|shchukin|barabanov|zimin|molchanov|glukhov|simonov|zemlyanov|biryukov|koltsov|shulgin|knyazev|lavrentiev|ustinov|gribov|vishnyakov|sazonov|bogomolov|zolotarev)\b",  # Russian surnames (romanized)
]

# English language patterns
ENGLISH_PATTERNS = [
    r"\b(john|robert|william|james|michael|david|richard|thomas|christopher|daniel|matthew|anthony|mark|donald|steven|paul|andrew|joshua|kenneth|kevin|brian|george|edward|ronald|timothy|jason|jeffrey|ryan|jacob|gary|nicholas|eric|jonathan|stephen|larry|justin|scott|brandon|benjamin|samuel|gregory|alexander|patrick|frank|raymond|jack|dennis|jerry|tyler|aaron|jose|henry|adam|douglas|nathan|peter|zachary|kyle|noah|alan|ethan|lucas|wayne|sean|hunter|mason|evan|austin|jeremy|joseph|max|carlos|isaac|chase|cooper|tristan|blake|carson|logan|caleb|connor|elijah|owen|trevor|ian)\b",
    r"\b(mary|patricia|jennifer|linda|elizabeth|barbara|susan|jessica|sarah|karen|nancy|lisa|betty|helen|sandra|donna|carol|ruth|sharon|michelle|laura|sarah|kimberly|deborah|dorothy|lisa|nancy|karen|betty|helen|sandra|donna|carol|ruth|sharon|michelle|laura|emily|kimberly|deborah|amy|angela|ashley|brenda|emma|olivia|cynthia|marie|janet|catherine|frances|christine|samantha|debra|rachel|carolyn|janet|virginia|maria|heather|diane|julie|joyce|victoria|kelly|christina|joan|evelyn|lauren|judith|megan|cheryl|andrea|hannah|jacqueline|martha|gloria|teresa|sara|janice|marie|julia|kathryn|louise|grace|judith|ann|diane|frances|julie|catherine|patricia|rose|jean|nancy|marie|virginia|kathryn|doris|emma|helen|alice|helen|gloria|margaret|donna|ruth|beverly|lisa|carolyn|janet|marie|catherine|samantha|jennifer|elizabeth|charlotte|ashley|natalie|michelle|alexis|nicole|vanessa|megan|victoria|melissa|stephanie|jessica|amanda|sarah|linda|susan|barbara|betty|helen|sandra|donna|carol|ruth|sharon|emily|olivia|deborah|nancy|karen|amy|angela|brenda|cynthia|marie|janet|catherine|frances|christine|debra|rachel|carolyn|virginia|maria|heather|diane|julie|joyce|kelly|christina|joan|evelyn|lauren|megan|cheryl|andrea|jacqueline|martha|teresa|sara|janice|julia|kathryn|louise|grace|ann|patricia|rose)\b",
    r"\b(smith|johnson|williams|brown|jones|garcia|miller|davis|rodriguez|martinez|hernandez|lopez|gonzalez|wilson|anderson|thomas|taylor|moore|jackson|martin|lee|perez|thompson|white|harris|sanchez|clark|ramirez|lewis|robinson|walker|young|allen|king|wright|scott|torres|nguyen|hill|flores|green|adams|nelson|baker|hall|rivera|campbell|mitchell|carter|roberts|gomez|phillips|evans|turner|diaz|parker|cruz|edwards|collins|reyes|stewart|morris|morales|murphy|cook|rogers|gutierrez|ortiz|morgan|cooper|peterson|bailey|reed|kelly|howard|ramos|kim|cox|ward|richardson|watson|brooks|chavez|wood|james|bennett|gray|mendoza|ruiz|hughes|price|alvarez|castillo|sanders|patel|myers|long|ross|foster|jimenez)\b",
]


@lru_cache(maxsize=1024)
def detect_language(name: str) -> Language:
    """Detect the most likely language of a name."""
    # Use heuristic detection primarily since langdetect
    # isn't reliable for short texts like names
    name_lower = name.lower()

    # Count matches for each language
    german_score = sum(
        1 for pattern in GERMAN_PATTERNS if re.search(pattern, name_lower)
    )
    french_score = sum(
        1 for pattern in FRENCH_PATTERNS if re.search(pattern, name_lower)
    )
    italian_score = sum(
        1 for pattern in ITALIAN_PATTERNS if re.search(pattern, name_lower)
    )
    spanish_score = sum(
        1 for pattern in SPANISH_PATTERNS if re.search(pattern, name_lower)
    )
    portuguese_score = sum(
        1 for pattern in PORTUGUESE_PATTERNS if re.search(pattern, name_lower)
    )
    russian_score = sum(
        1 for pattern in RUSSIAN_PATTERNS if re.search(pattern, name_lower)
    )
    chinese_score = sum(
        1 for pattern in CHINESE_PATTERNS if re.search(pattern, name_lower)
    )
    arabic_score = sum(
        1 for pattern in ARABIC_PATTERNS if re.search(pattern, name_lower)
    )
    english_score = sum(
        1 for pattern in ENGLISH_PATTERNS if re.search(pattern, name_lower)
    )

    # Enhanced logic for language detection
    # Strong language indicators
    has_french_accents = bool(re.search(r"ç|è|é|ê|à|ù|û|î|ô|ë|ï|ÿ", name_lower))
    has_french_particles = bool(
        re.search(r"\b(du|des|le|la|les|d')\b", name_lower)
    )  # Removed "de" to avoid Spanish confusion
    has_french_compound = bool(re.search(r"\w+-\w+", name))  # hyphenated compounds

    # Specific French name indicators (removed ambiguous names like "robert", "marie", etc.)
    has_french_names = bool(
        re.search(
            r"\b(françois|jean|pierre|michel|andré|jacques|henri|philippe|patrice|claude|bernard|alain|christian|christophe|olivier|nicolas|laurent|thierry|pascal|frédéric|sébastien|antoine|emmanuel|vincent|stéphane|dominique|julien|bruno|eric|fabrice|didier|gérard|rené|roger|yves|maurice|marcel|louis|francis|lucien|albert|raymond|gabriel|gilbert|paul|andre|denis|gerard|joseph|rené|lucien|gabriel|francis|albert|raymond|paul|louis|simon|xavier|edouard|georges|charles|didier|françoise|monique|sylvie|isabelle|catherine|christine|brigitte|martine|véronique|nicole|nathalie|chantal|danielle|jacqueline|michèle|annie|joséphine|marguerite|jeanne|denise|simone|madeleine|suzanne|andrée|louise|marcelle|hélène|georgette|yvette|germaine|thérèse|bernadette|paulette|solange|ginette|colette|odette|huguette|pierrette|arlette|gisèle|josette|lucette|marceline|henriette|antoinette|elisabeth|elise|claire|sylvie|anne|anna)\b",
            name_lower,
        )
    )

    has_german_umlauts = bool(re.search(r"ß|ä|ö|ü", name_lower))
    has_german_particles = bool(
        re.search(r"\b(von|van|der|zu|zur|am|im)\b", name_lower)
    )

    has_italian_accents = bool(re.search(r"[àèéìíîòóùú]", name_lower))
    has_italian_particles = bool(
        re.search(
            r"\b(di|del|della|dei|delle|dello|degli|da|dal|dalla|dallo|dalle|san|santa|santo)\b",
            name_lower,
        )
    )

    # More specific Italian indicators
    has_italian_names = bool(
        re.search(
            r"\b(alessandro|andrea|antonio|carlo|francesco|giovanni|giuseppe|lorenzo|luca|marco|matteo|michele|paolo|roberto|stefano|alberto|angelo|bruno|claudio|daniele|davide|emanuele|enrico|fabio|federico|filippo|franco|gabriele|giacomo|giorgio|giulio|leonardo|luigi|mario|massimo|maurizio|nicola|pietro|riccardo|salvatore|sergio|simone|tommaso|umberto|vincenzo|alessandra|anna|antonella|barbara|carla|caterina|chiara|cristina|daniela|elena|elisabetta|federica|francesca|giovanna|giulia|giuseppina|laura|lucia|luisa|manuela|margherita|maria|marina|marta|michela|monica|paola|patrizia|raffaella|rita|roberta|rosa|rosanna|sara|serena|silvia|simona|stefania|teresa|valentina|valeria)\b",
            name_lower,
        )
    )
    has_italian_surnames = bool(
        re.search(
            r"\b(rossi|russo|ferrari|esposito|bianchi|romano|colombo|ricci|marino|greco|bruno|gallo|conti|costa|giordano|mancini|rizzo|lombardi|moretti|barbieri|fontana|santoro|mariani|rinaldi|caruso|ferrara|galli|martini|leone|longo|gentile|martinelli|vitale|lombardo|serra|coppola|marchetti|parisi|villa|conte|ferretti|pellegrini|palumbo|sanna|fabbri|montanari|grassi|giuliani|benedetti|barone|rossetti|caputo|montanaro|guerra|palmieri|bernardi|martino|fiore|mazza|silvestri|testa|pellegrino|carbone|giuliano|benedetto|donati|ruggiero|orlando|ferri|cattaneo|bianco|valentini|pagano|sorrentino|basile|santini|ferraro|farina|rizzi|morelli|amato|milani|cattaneo)\b",
            name_lower,
        )
    )

    has_spanish_accents = bool(re.search(r"[áéíóúüñ]", name_lower))
    has_spanish_particles = bool(
        re.search(
            r"\b(de|del|de la|de las|de los|y|e|san|santa|santo|da|das|dos|do)\b",
            name_lower,
        )
    )

    # More specific Spanish indicators
    has_spanish_names = bool(
        re.search(
            r"\b(josé|maría|francisco|carlos|ana|juan|luis|manuel|antonio|jesús|pedro|rafael|miguel|alejandro|diego|fernando|jorge|ricardo|roberto|sergio|vicente|adrián|alberto|alfonso|andrés|ángel|arturo|eduardo|emilio|enrique|guillermo|ignacio|jaime|leonardo|lorenzo|marcos|mario|martín|nicolás|oscar|raúl|rubén|salvador|santiago|tomás|víctor|carmen|josefa|isabel|dolores|pilar|teresa|rosa|francisca|antonia|mercedes|esperanza|ángeles|concepción|manuela|elena|cristina|patricia|laura|marta|beatriz|silvia|mónica|andrea|lucía|raquel|sara|natalia|alejandra|paula|eva|rocío|julia|esther|irene|nuria|susana|yolanda|amparo|gloria|inmaculada|montserrat|remedios|encarnación|rosario|consuelo|soledad|asunción|milagros|nieves|aurora|blanca|estrella|lourdes|marisol|noelia|paloma|sonia|verónica)\b",
            name_lower,
        )
    )
    has_spanish_surnames = bool(
        re.search(
            r"\b(garcía|rodríguez|gonzález|fernández|lópez|martínez|sánchez|pérez|gómez|martín|jiménez|ruiz|hernández|díaz|moreno|álvarez|muñoz|romero|alonso|gutiérrez|navarro|torres|domínguez|vázquez|ramos|gil|ramírez|serrano|blanco|suárez|molina|morales|ortega|delgado|castro|ortiz|rubio|marín|sanz|iglesias|medina|garrido|cortés|castillo|santos|lozano|guerrero|cano|prieto|méndez|cruz|herrera|peña|flores|cabrera|campos|vega|fuentes|carrasco|diez|caballero|reyes|nieto|aguilar|pascual|herrero|montero|lorenzo|hidalgo|giménez|ibáñez|ferrer|duran|santiago|benítez|mora|vicente|vargas|arias|carmona|crespo|román|pastor|soto|sáez|velasco|moya|soler|parra|esteban|bravo|gallego|rojas|estévez|vidal|molina|león|peña|mendoza|guerrero|medina|cortés|contreras|jiménez|herrera|guzmán|vargas|castillo|ramírez|torres|flores|rivera|gómez|díaz|cruz|morales|reyes|gutiérrez|ortiz|chávez|ramos|herrera|méndez|ruiz|álvarez|vásquez|castillo|moreno|romero|herrera|medina|guerrero|cruz|ortega|gómez|vargas|gonzález|pérez|sánchez|ramírez|torres|rivera|flores)\b",
            name_lower,
        )
    )

    # Check for Portuguese indicators
    has_portuguese_tildes = bool(
        re.search(r"[ãõ]", name_lower)
    )  # Very Portuguese-specific
    has_portuguese_particles = bool(
        re.search(r"\b(dos|são|da costa|da silva|dos santos)\b", name_lower)
    )  # Very specific Portuguese particles and common combinations
    has_portuguese_names = bool(
        re.search(
            r"\b(joão|antónio|antônio|gonçalo|goncalo|conceição|conceicao|rui|hugo|tiago|sérgio|sergio|nuno|diogo|bernardo|rodrigo|filipe|felipe|guilherme|renato|márcio|marcio|fábio|fabio|júlio|julio|césar|cesar|adriano|cristiano|leandro|flávio|flavio|caio|mateus|luciano|thiago|catarina|joana|teresa|tereza|francisca|luísa|luisa|beatriz|inês|inez|patricia|rita|vera|sílvia|silvia|fernanda|raquel|mónica|monica|susana|cláudia|claudia|célia|celia|fátima|fatima|helena|manuela|lurdes|glória|gloria|graça|graca|eduarda|bárbara|barbara|margarida|marlene|filipa|olívia|olivia|lúcia|lucia|rute|vitória|victoria|leonor|bruna|sónia|sonia|vanessa|carolina|daniela|andreia|andréia|liliana|anabela|tânia|tania)\b",
            name_lower,
        )
    )
    has_portuguese_surnames = bool(
        re.search(
            r"\b(silva|santos|ferreira|pereira|oliveira|costa|rodrigues|martins|jesus|sousa|fernandes|gonçalves|gomes|lopes|marques|alves|almeida|ribeiro|pinto|carvalho|teixeira|moreira|correia|mendes|nunes|soares|vieira|monteiro|cardoso|rocha|neves|coelho|cunha|pires|reis|antunes|machado|miranda|castro|lima|henriques|dias|caetano|fonseca|morais|magalhães|valente|pacheco|esteves|tavares|barros|carneiro|guedes|freitas|barbosa|faria|sá|brito|leite|melo)\b",
            name_lower,
        )
    )

    # Check for Chinese indicators
    has_chinese_characters = bool(
        re.search(r"[\u4e00-\u9fff\u3400-\u4dbf]", name_lower)
    )
    has_chinese_surnames = bool(
        re.search(
            r"\b(wang|li|zhang|liu|chen|yang|huang|zhao|zhou|wu|xu|sun|zhu|ma|hu|guo|lin|he|gao|liang|zheng|luo|song|xie|tang|han|cao|deng|xiao|feng|zeng|cheng|cai|peng|pan|yuan|yu|dong|su|ye|wei|jiang|tian|du|ding|shen|fan|fu|zhong|lu|dai|cui|ren|liao|yao|fang|jin|qiu|xia|tan|zou|shi|xiong|meng|qin|yan|xue|hou|lei|bai|long|duan|hao|kong|shao|mao|chang|wan|gu|lai|wu|kang|he|yan|yin|qian|niu|hong|gong|wong|lee|chang|lau|chan|yeung|chiu|chow|ng|tsui|soon|chu|mah|woo|kwok|lam|ho|ko|leung|cheng|law|sung|tse|tong|hon|tso|hui|siu|fung|tsang|ching|choy|pang|poon|yuen|tung|so|yip|lui|wai|cheung|tin|to|ting|sum|keung|fan|kong|foo|chung|lou|toy|chui|yam|luk|liu|yiu|fong|kam|yau|har|tam|kar|chau|sek|hung|mang|chun|yim|sit|hau|pak|lung|tuen|see|mou|sheung|man|koo|loi|mo|hor|wan|chin|ngau|kung)\b",
            name_lower,
        )
    )
    bool(
        re.search(
            r"\b(wei|ming|hua|jian|jun|lei|tao|chao|bin|hui|gang|peng|fei|kai|jie|liang|long|zhi|hai|dong|yang|chun|hao|tian|wen|wu|kang|jian|hong|bo|li|hong|xia|yan|juan|fang|mei|ling|jing|min|ping|lan|ying|xue|lin|ying|jie|xiu|hua|yue|ning|yu|ting|jing|xin|qian|na|yao|lei|wei|zhen|qin|yun|feng|lu|jia)\b",
            name_lower,
        )
    )

    # Check for Arabic indicators
    has_arabic_script = bool(
        re.search(r"[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]", name_lower)
    )
    has_arabic_particles = bool(
        re.search(r"\b(al|el|ibn|bin|bint|abu|um|abd)\b", name_lower)
    )
    has_arabic_names = bool(
        re.search(
            r"\b(muhammad|mohamed|mohammed|mohammad|ahmad|ahmed|ali|abdullah|abdallah|omar|umar|yusuf|yousef|ibrahim|hassan|hussein|khalid|khaled|salem|salim|mansour|mahmoud|amr|saeed|said|nasser|waleed|walid|osama|tariq|faisal|adel|rami|samer|karim|hakim|marwan|mazen|majed|nabil|wael|ziad|riad|adnan|jamal|maged|hatim|hazem|tamer|bassam|fatima|fatma|aisha|aysha|khadija|mariam|maryam|zainab|zaynab|safiya|hafsa|ruqayya|asma|salma|nour|noor|rana|rania|dina|hala|layla|laila|hanan|mona|muna|reem|rim|noha|ghada|sawsan|widad|siham|nawal|amina|samira|karima|wafa|maha|suad|najwa|thuraya|farah|dalia|yasmin|yasmeen|leena|lina|tala|lara|maya|sara|sarah|jana)\b",
            name_lower,
        )
    )

    # Check for Russian indicators
    has_cyrillic_script = bool(
        re.search(r"[\u0400-\u04FF\u0500-\u052F\u2DE0-\u2DFF\uA640-\uA69F]", name_lower)
    )
    has_russian_patronymic = bool(
        re.search(
            r"(ович|евич|ич|овна|евна|ична|ovich|evich|ich|ovna|evna|ichna)$",
            name_lower,
        )
    )
    has_russian_names = bool(
        re.search(
            r"\b(александр|алексей|андрей|антон|артем|борис|владимир|дмитрий|евгений|игорь|иван|константин|максим|михаил|николай|олег|павел|петр|роман|сергей|анна|елена|ирина|мария|наталья|ольга|светлана|татьяна|юлия|екатерина|aleksandr|aleksey|andrey|anton|artem|boris|vladimir|dmitriy|evgeniy|igor|ivan|konstantin|maksim|mikhail|nikolay|oleg|pavel|petr|roman|sergey|anna|elena|irina|mariya|natalya|olga|svetlana|tatyana|yuliya|ekaterina|alexander|alexey|andrew|anthony|arthur|michael|nicholas|peter|sergei|natasha|katya|sasha|misha|dima|vova|kolya|pasha|roma|max|maxim)\b",
            name_lower,
        )
    )
    has_russian_surnames = bool(
        re.search(
            r"\b(иванов|петров|сидоров|смирнов|кузнецов|попов|лебедев|козлов|новиков|морозов|волков|соловьев|васильев|зайцев|павлов|семенов|голубев|виноградов|богданов|воробьев|федоров|михайлов|беляев|тарасов|белов|комаров|орлов|киселев|макаров|андреев|ковалев|ильин|гусев|титов|кузьмин|кудрявцев|баранов|куликов|алексеев|степанов|яковлев|сорокин|сергеев|романов|захаров|борисов|королев|герасимов|пономарев|григорьев|лазарев|медведев|ершов|никитин|соболев|рябов|поляков|цветков|данилов|жуков|фролов|журавлев|николаев|крылов|максимов|осипов|белоусов|федотов|дорофеев|егоров|матвеев|бобров|дмитриев|калинин|анисимов|петухов|антонов|тимофеев|никифоров|веселов|филиппов|марков|большаков|суханов|миронов|ширяев|александров|коновалов|шестаков|казаков|ефимов|денисов|громов|фомин|давыдов|мельников|щербаков|блинов|колесников|карпов|афанасьев|власов|маслов|исаков|тихонов|аксенов|гаврилов|родионов|котов|горбунов|кудряшов|быков|зуев|третьяков|савельев|панов|рыбаков|суворов|абрамов|воронов|мухин|архипов|трофимов|мартынов|емельянов|горшков|чернов|овчинников|селезнев|панфилов|копылов|михеев|галкин|назаров|лобанов|лукин|беляков|потапов|некрасов|хохлов|жданов|наумов|шилов|воронцов|ермаков|дроздов|игнатьев|савин|логинов|сафонов|капустин|кириллов|моисеев|елисеев|кошелев|костин|горбачев|орехов|ефремов|исаев|евдокимов|калашников|кабанов|носков|юдин|кулагин|лапин|прохоров|нестеров|харитонов|агафонов|муравьев|ларионов|матюшин|дементьев|гуляев|борисенко|прокофьев|шаров|мясников|лыткин|большов|краснов|рыжов|сычев|батурин|стрелков|пестов|русаков|стариков|щукин|барабанов|зимин|молчанов|глухов|симонов|землянов|бирюков|кольцов|шульгин|князев|лаврентьев|устинов|грибов|вишняков|сазонов|богомолов|золотарев|ivanov|petrov|sidorov|smirnov|kuznetsov|popov|lebedev|kozlov|novikov|morozov|volkov|solovyov|vasiliev|zaitsev|pavlov|semenov|golubev|vinogradov|bogdanov|vorobyov|fedorov|mikhailov|belyaev|tarasov|belov|komarov|orlov|kiselev|makarov|andreev|kovalev|ilyin|gusev|titov|kuzmin|kudryavtsev|baranov|kulikov|alekseev|stepanov|yakovlev|sorokin|sergeev|romanov|zakharov|borisov|korolev|gerasimov|ponomarev|grigoriev|lazarev|medvedev|ershov|nikitin|sobolev|ryabov|polyakov|tsvetkov|danilov|zhukov|frolov|zhuravlev|nikolaev|krylov|maksimov|osipov|belousov|fedotov|dorofeev|egorov|matveev|bobrov|dmitriev|kalinin|anisimov|petukhov|antonov|timofeev|nikiforov|veselov|filippov|markov|bolshakov|sukhanov|mironov|shiryaev|aleksandrov|konovalov|shestakov|kazakov|efimov|denisov|gromov|fomin|davydov|melnikov|shcherbakov|blinov|kolesnikov|karpov|afanasiev|vlasov|maslov|isakov|tikhonov|aksenov|gavrilov|rodionov|kotov|gorbunov|kudryashov|bykov|zuev|tretyakov|saveliev|panov|rybakov|suvorov|abramov|voronov|mukhin|arkhipov|trofimov|martynov|emelyanov|gorshkov|chernov|ovchinnikov|seleznev|panfilov|kopylov|mikheev|galkin|nazarov|lobanov|lukin|belyakov|potapov|nekrasov|khokhlov|zhdanov|naumov|shilov|vorontsov|ermakov|drozdov|ignatiev|savin|loginov|safonov|kapustin|kirillov|moiseev|eliseev|koshelev|kostin|gorbachev|orekhov|efremov|isaev|evdokimov|kalashnikov|kabanov|noskov|yudin|kulagin|lapin|prokhorov|nesterov|kharitonov|agafonov|muraviev|larionov|matyushin|dementiev|gulyaev|borisenko|prokofiev|biryukov|sharov|myasnikov|lytkin|bolshov|krasnov|ryzhov|sychev|baturin|strelkov|pestov|rusakov|starikov|shchukin|barabanov|zimin|molchanov|glukhov|simonov|zemlyanov|biryukov|koltsov|shulgin|knyazev|lavrentiev|ustinov|gribov|vishnyakov|sazonov|bogomolov|zolotarev)\b",
            name_lower,
        )
    )

    # Check for Russian female surname patterns (male surname + 'a')
    has_russian_female_surnames = bool(
        re.search(
            r"\b(иванова|петрова|сидорова|смирнова|кузнецова|попова|лебедева|козлова|новикова|морозова|волкова|соловьева|васильева|зайцева|павлова|семенова|голубева|виноградова|богданова|воробьева|федорова|михайлова|беляева|тарасова|белова|комарова|орлова|киселева|макарова|андреева|ковалева|ильина|гусева|титова|кузьмина|кудрявцева|баранова|куликова|алексеева|степанова|яковлева|сорокина|сергеева|романова|захарова|борисова|королева|герасимова|пономарева|григорьева|лазарева|медведева|ершова|никитина|соболева|рябова|полякова|цветкова|данилова|жукова|фролова|журавлева|николаева|крылова|максимова|осипова|белоусова|федотова|дорофеева|егорова|матвеева|боброва|дмитриева|калинина|анисимова|петухова|антонова|тимофеева|никифорова|веселова|филиппова|маркова|большакова|суханова|миронова|ширяева|александрова|коноваловa|шестакова|казакова|ефимова|денисова|громова|фомина|давыдова|мельникова|щербакова|блинова|колесникова|карпова|афанасьева|власова|маслова|исакова|тихонова|аксенова|гаврилова|родионова|котова|горбунова|кудряшова|быкова|зуева|третьякова|савельева|панова|рыбакова|суворова|абрамова|воронова|мухина|архипова|трофимова|мартынова|емельянова|горшкова|чернова|овчинникова|селезнева|панфилова|копылова|михеева|галкина|назарова|лобанова|лукина|белякова|потапова|некрасова|хохлова|жданова|наумова|шилова|воронцова|ермакова|дроздова|игнатьева|савина|логинова|сафонова|капустина|кириллова|моисеева|елисеева|кошелева|костина|горбачева|орехова|ефремова|исаева|евдокимова|калашникова|кабанова|носкова|юдина|кулагина|лапина|прохорова|нестерова|харитонова|агафонова|муравьева|ларионова|матюшина|дементьева|гуляева|борисенко|прокофьева|шарова|мясникова|лыткина|большова|краснова|рыжова|сычева|батурина|стрелкова|пестова|русакова|старикова|щукина|барабанова|зимина|молчанова|глухова|симонова|землянова|бирюкова|кольцова|шульгина|князева|лаврентьева|устинова|грибова|вишнякова|сазонова|богомолова|золотарева|ivanova|petrova|sidorova|smirnova|kuznetsova|popova|lebedeva|kozlova|novikova|morozova|volkova|solovyova|vasilieva|zaitseva|pavlova|semenova|golubeva|vinogradova|bogdanova|vorobyova|fedorova|mikhailova|belyaeva|tarasova|belova|komarova|orlova|kiseleva|makarova|andreeva|kovaleva|ilyina|guseva|titova|kuzmina|kudryavtseva|baranova|kulikova|alekseeva|stepanova|yakovleva|sorokina|sergeeva|romanova|zakharova|borisova|koroleva|gerasimova|ponomareva|grigorieva|lazareva|medvedeva|ershova|nikitina|soboleva|ryabova|polyakova|tsvetkova|danilova|zhukova|frolova|zhuravleva|nikolaeva|krylova|maksimova|osipova|belousova|fedotova|dorofeeva|egorova|matveeva|bobrova|dmitrieva|kalinina|anisimova|petukhova|antonova|timofeeva|nikiforova|veselova|filippova|markova|bolshakova|sukhanova|mironova|shiryaeva|aleksandrova|konovalova|shestakova|kazakova|efimova|denisova|gromova|fomina|davydova|melnikova|shcherbakova|blinova|kolesnikova|karpova|afanasieva|vlasova|maslova|isakova|tikhonova|aksenova|gavrilova|rodionova|kotova|gorbunova|kudryashova|bykova|zueva|tretyakova|savelieva|panova|rybakova|suvorova|abramova|voronova|mukhina|arkhipova|trofimova|martynova|emelyanova|gorshkova|chernova|ovchinnikova|selezneva|panfilova|kopylova|mikheeva|galkina|nazarova|lobanova|lukina|belyakova|potapova|nekrasova|khokhlova|zhdanova|naumova|shilova|vorontsova|ermakova|drozdova|ignatieva|savina|loginova|safonova|kapustina|kirillova|moiseeva|eliseeva|kosheleva|kostina|gorbacheva|orekhova|efremova|isaeva|evdokimova|kalashnikova|kabanova|noskova|yudina|kulagina|lapina|prokhorova|nesterova|kharitonova|agafonova|muravieva|larionova|matyushina|dementieva|gulyaeva|borisenko|prokofieva|sharova|myasnikova|lytkina|bolshova|krasnova|ryzhova|sycheva|baturina|strelkova|pestova|rusakova|starikova|shchukina|barabanova|zimina|molchanova|glukhova|simonova|zemlyanova|biryukova|koltsova|shulgina|knyazeva|lavrentieva|ustinova|gribova|vishnyakova|sazonova|bogomolova|zolotareva)\b",
            name_lower,
        )
    )

    # Check for English indicators
    has_english_names = bool(
        re.search(
            r"\b(john|robert|william|james|michael|david|richard|thomas|christopher|daniel|matthew|anthony|mark|donald|steven|paul|andrew|joshua|kenneth|kevin|brian|george|edward|ronald|timothy|jason|jeffrey|ryan|jacob|gary|nicholas|eric|jonathan|stephen|larry|justin|scott|brandon|benjamin|samuel|gregory|alexander|patrick|frank|raymond|jack|dennis|jerry|tyler|aaron|henry|adam|douglas|nathan|peter|zachary|kyle|noah|alan|ethan|lucas|wayne|sean|hunter|mason|evan|austin|jeremy|joseph|max|isaac|chase|cooper|tristan|blake|carson|logan|caleb|connor|elijah|owen|trevor|ian|mary|patricia|jennifer|linda|elizabeth|barbara|susan|jessica|sarah|karen|nancy|lisa|betty|helen|sandra|donna|carol|ruth|sharon|michelle|laura|emily|kimberly|deborah|amy|angela|ashley|brenda|emma|olivia|cynthia|janet|catherine|frances|christine|samantha|debra|rachel|carolyn|virginia|heather|diane|julie|joyce|victoria|kelly|christina|joan|evelyn|lauren|judith|megan|cheryl|andrea|hannah|jacqueline|martha|gloria|teresa|sara|janice|julia|kathryn|louise|grace|ann|rose)\b",
            name_lower,
        )
    )
    has_english_surnames = bool(
        re.search(
            r"\b(smith|johnson|williams|brown|jones|miller|davis|wilson|anderson|thomas|taylor|moore|jackson|martin|lee|thompson|white|harris|clark|lewis|robinson|walker|young|allen|king|wright|scott|hill|green|adams|nelson|baker|hall|rivera|campbell|mitchell|carter|roberts|phillips|evans|turner|parker|edwards|collins|stewart|morris|murphy|cook|rogers|morgan|cooper|peterson|bailey|reed|kelly|howard|cox|ward|richardson|watson|brooks|wood|james|bennett|gray|hughes|price|myers|long|ross|foster)\b",
            name_lower,
        )
    )

    # Decision logic with stronger preferences
    # Chinese, Arabic, and Russian get highest priority due to distinctive scripts
    if has_chinese_characters or (has_chinese_surnames and chinese_score >= 1):
        return Language.MANDARIN
    elif has_arabic_script or has_arabic_names or arabic_score >= 1:
        return Language.ARABIC
    elif (
        has_cyrillic_script
        or has_russian_patronymic
        or has_russian_surnames
        or has_russian_female_surnames
        or (has_russian_names and russian_score >= 1)
    ):
        return Language.RUSSIAN
    elif has_german_umlauts or (has_german_particles and german_score >= 1):
        return Language.GERMAN
    elif (
        has_portuguese_tildes
        or has_portuguese_particles
        or (has_portuguese_names and portuguese_score >= 1)
    ):
        return Language.PORTUGUESE
    elif has_french_accents and (
        has_french_particles
        or has_french_compound
        or has_french_names
        or french_score >= 1
    ):
        return Language.FRENCH
    elif has_italian_particles and (
        has_italian_names or has_italian_surnames or italian_score >= 1
    ):
        return Language.ITALIAN
    elif has_spanish_accents or has_spanish_names or has_spanish_surnames:
        return Language.SPANISH
    elif has_arabic_particles and arabic_score >= 1:
        return Language.ARABIC
    elif has_spanish_particles and spanish_score >= 1:
        return Language.SPANISH
    elif has_italian_accents or has_italian_names or has_italian_surnames:
        return Language.ITALIAN
    elif has_french_particles or has_french_compound or has_french_names:
        return Language.FRENCH
    elif has_portuguese_surnames and portuguese_score >= 1:
        return Language.PORTUGUESE
    elif has_english_names or has_english_surnames or english_score >= 1:
        return Language.ENGLISH
    elif arabic_score >= 2:
        return Language.ARABIC
    elif russian_score >= 2:
        return Language.RUSSIAN
    elif german_score >= 2:
        return Language.GERMAN
    elif portuguese_score >= 2:
        return Language.PORTUGUESE
    elif french_score >= 2:
        return Language.FRENCH
    elif italian_score >= 2:
        return Language.ITALIAN
    elif spanish_score >= 2:
        return Language.SPANISH

    # Try langdetect as fallback but be conservative
    try:
        if len(name.split()) >= 2:  # For multi-word names
            try:
                from langdetect import detect_langs  # type: ignore
            except ImportError:
                # langdetect not available, skip this fallback
                pass
            else:
                langs = detect_langs(name)

                # Only use if confidence is reasonably high
                if langs and langs[0].prob > 0.7:
                    detected = langs[0].lang
                    language_map = {
                        "fr": Language.FRENCH,
                        "de": Language.GERMAN,
                        "en": Language.ENGLISH,
                        "it": Language.ITALIAN,
                        "es": Language.SPANISH,
                        "pt": Language.PORTUGUESE,
                        "ar": Language.ARABIC,
                        "ru": Language.RUSSIAN,
                    }
                    if detected in language_map:
                        return language_map[detected]

    except Exception:
        # LangDetectException or any other exception from langdetect
        pass

    # Default to English - most names will work fine with English rules
    return Language.ENGLISH
