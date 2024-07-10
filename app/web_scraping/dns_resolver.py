import dns.resolver

def get_subdomains(domain):
    subdomains = set()
    resolver = dns.resolver.Resolver()
    
    # Extended list of common subdomain prefixes
    prefixes = [
        'www', 'demo',
        'docs', 'download', 'forum', 'help', 'info', 'news', 'test', 'vpn', 'ww1',
        'owa', 'store', 'web', 'webdisk', 'imap', 'lms', 'home', 'cpanel', 'whm',
        'admin', 'net', 'it', 'students', 'faculty', 'dining', 'library', 'services',
        'careers', 'jobs', 'campus', 'events', 'calendar', 'admissions', 'research',
        'alumni', 'giving', 'academics', 'departments', 'athletics', 'sports', 'health',
        'medical', 'clinic', 'patient', 'clinic', 'finance', 'hr', 'humanresources',
        'intranet', 'intra', 'gov', 'government', 'legal', 'law', 'justice', 'maps',
        'media', 'newsroom', 'newsletter', 'parking', 'police', 'security', 'public',
        'relations', 'safety', 'transit', 'transport', 'tv', 'video', 'virtual', 'wifi',
        'wireless', 'cloud', 'compute', 'database', 'db', 'storage', 'backup', 'docs',
        'api', 'api-docs', 'staging', 'qa', 'dev', 'development', 'prod', 'production',
        'tax', 'legal', 'compliance', 'audit', 'facilities', 'maintenance', 'hr', 'jobs',
        'interns', 'internships', 'careers', 'recruitment', 'talent', 'apply', 'applications',
        'tickets', 'billing', 'invoice', 'pay', 'payment', 'checkout', 'store', 'shop',
        'order', 'orders', 'cart', 'basket', 'customer', 'support', 'service', 'helpdesk',
        'help', 'assistance', 'faq', 'knowledgebase', 'kb', 'wiki', 'docs', 'documentation',
        'guides', 'manuals', 'tutorials', 'resources', 'learning', 'training', 'courses',
        'classroom', 'school', 'college', 'department', 'office', 'faculty', 'staff', 'students',
        'alumni', 'graduates', 'undergraduates', 'freshmen', 'sophomores', 'juniors', 'seniors',
        'exchange', 'abroad', 'international', 'visa', 'immigration', 'library', 'books', 'journal',
        'publication', 'repository', 'archive', 'collection', 'museum', 'gallery', 'exhibition', 'art',
        'science', 'technology', 'engineering', 'math', 'stem', 'medicine', 'law', 'business', 'economics',
        'psychology', 'sociology', 'anthropology', 'history', 'geography', 'literature', 'languages', 'philosophy',
        'theology', 'religion', 'culture', 'politics', 'government', 'environment', 'ecology', 'biology', 'chemistry',
        'physics', 'astronomy', 'geology', 'earth', 'planet', 'space', 'ocean', 'marine', 'climate', 'weather', 'forecast',
        'disaster', 'emergency', 'response', 'rescue', 'relief', 'aid', 'charity', 'nonprofit', 'ngo', 'volunteer', 'community',
        'social', 'justice', 'equality', 'rights', 'advocacy', 'campaign', 'movement', 'initiative', 'project', 'program', 'taskforce'
        'catalog','registrar','schedule','policy','procedure','standard','guideline','requirement','specification','manual','handbook',
        'enroll','registration','admission','tuition','fee','payment','financial','aid','scholarship','grant','loan','refund','transcript',
        'degree','diploma','certificate','major','minor','concentration','course','class','module','lesson','lecture','homework','assignment',
        'sciences','engineering','technology','mathematics','arts','humanities','social','sciences','business','administration','management',
        'medical','health','nursing','pharmacy','dental','law','legal','justice','criminal','psychology','counseling','sociology','anthropology',
        'diversity','inclusion','equity','accessibility','disability','accommodation','international','global','study','abroad','exchange',
        'jobs','internships','careers','employment','opportunities','work','study','research','projects','publications','news','events','calendar',
        'online','distance','learning','elearning','virtual','remote','hybrid','blended','synchronous','asynchronous','live','recorded',
        'military','veterans','service','members','dependents','benefits','resources','support','counseling','advising','tutoring','mentoring',
        'intramurals','sports','recreation','fitness','wellness','health','nutrition','counseling','medical','clinic','pharmacy','counseling',
        'academicaffairs','provost','dean','faculty','staff','students','parents','alumni','donors','friends','partners','community','relations',
        'careercenter','careers','jobs','graduation','commencement','ceremony','honors','awards','recognition','scholarships','fellowships',
        'studentsuccess', 'advising', 'counseling', 'mentoring', 'tutoring', 'coaching', 'support', 'resources', 'services', 'programs',
        'studentlife', 'studentaffairs', 'studentresources', 'studentactivities', 'studentorganizations', 'clubs', 'events', 'activities',
    ]
    
    for prefix in prefixes:
        try:
            subdomain = f"{prefix}.{domain}"
            answers = resolver.resolve(subdomain, 'A')
            for answer in answers:
                subdomains.add(subdomain)
        except dns.resolver.NoAnswer:
            continue
        except dns.resolver.NXDOMAIN:
            continue
        except dns.resolver.Timeout:
            continue
        except dns.exception.DNSException as e:
            print(f"An error occurred: {e}")
            continue
    
    return subdomains

def find_all_subdomains(domain):

# Get subdomains
    subdomains = get_subdomains(domain)
    start_urls = [{"url": f"https://{subdomain}"} for subdomain in subdomains]
    return start_urls
