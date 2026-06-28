import os
import sys
import sqlite3

# Define rich blogs data
blogs_data = [
    {
        "id": 1,
        "title": "Empowering Youth for a Sustainable Future",
        "slug": "empowering-youth-for-a-sustainable-future",
        "author": "Pink Cycle Team",
        "content": """### The Power of Youth
Youth are the leaders of tomorrow, but more importantly, they are active changemakers today. In our recent community workshop, we gathered young minds from across the region to discuss how youth can drive sustainable development within their local neighborhoods. The energy was electric as ideas flowed around recycling initiatives, solar energy adoption, and waste reduction.

### Local Solutions for Global Problems
Sustainable development isn't just about global policy; it starts with grassroots action. We explored practical, low-cost projects that youth groups can implement immediately. For instance, launching community gardens not only provides fresh organic produce but also creates green spaces that improve local biodiversity and air quality.

### Action Plan and Commitment
By the end of the seminar, the attendees committed to forming 'Green Cells' in their schools and estates. These cells will spearhead monthly clean-up drives, tree planting activities, and educational campaigns. The future is green, and it is firmly in the hands of our empowered youth.""",
        "image": "blogs/youth.jpeg",
        "image_description": "A group of young leaders discussing sustainable development goals.",
        "event_description": "Community Workshop - June 2026",
    },
    {
        "id": 2,
        "title": "Digital Skills for the Modern Era",
        "slug": "digital-skills-for-the-modern-era",
        "author": "Pink Cycle Team",
        "content": """### Breaking the Digital Divide
In today’s hyper-connected world, technology is the ultimate tool for economic and social empowerment. Yet, millions of young people remain disconnected from the digital economy due to a lack of access and skills. Our recent Tech Empowerment Boot Camp aimed to bridge this gap by providing hands-on training to underprivileged youth.

### From Consumption to Creation
The boot camp shifted the participants' perspective from being passive consumers of technology to active creators. Over five days, they learned the fundamentals of web development, digital marketing, and computer literacy. Building their first web pages gave them a tangible sense of achievement and a glimpse into career paths in the global tech sector.

### Building Future Careers
Beyond technical skills, we provided mentorship on career opportunities in software development, graphic design, and freelance digital work. By equipping these youth with modern digital tools, we are unlocking doors to employment and entrepreneurial paths that were previously out of reach.""",
        "image": "blogs/youth1.jpeg",
        "image_description": "Students working on computers during a coding workshop.",
        "event_description": "Tech Empowerment Boot Camp - June 2026",
    },
    {
        "id": 3,
        "title": "Health and Wellness in Urban Communities",
        "slug": "health-and-wellness-in-urban-communities",
        "author": "Pink Cycle Team",
        "content": """### Prioritizing Mental Health
Living in fast-paced urban environments can take a toll on physical and emotional well-being. Our Wellness Saturday seminar focused on the crucial but often ignored topic of mental health and physical fitness among young adults. We created a safe space for open conversations about stress, anxiety, and depression.

### Holistic Well-being
True wellness requires a holistic approach that connects the mind and body. Professional fitness coaches led participants through accessible physical exercises, while mental health experts introduced mindfulness techniques and breathing exercises to manage daily stress. The emphasis was on building healthy, sustainable daily routines.

### Community Support Systems
We concluded the event by establishing peer support groups. Participants left with practical toolkits for self-care and contact details for professional mental health services. Breaking the stigma around mental health is a community effort, and this wellness seminar was a major step in that direction.""",
        "image": "blogs/youth2.jpeg",
        "image_description": "A yoga and mindfulness session in an urban park.",
        "event_description": "Wellness Saturday - June 2026",
    },
    {
        "id": 4,
        "title": "Voices of the Future: Leadership Seminar",
        "slug": "voices-of-the-future-leadership-seminar",
        "author": "Pink Cycle Team",
        "content": """### Cultivating Ethical Leadership
Leadership is not about holding a title or exercising authority; it is about service, empathy, and integrity. The Annual Leadership Conference brought together seasoned mentors and aspiring young leaders to discuss what it means to lead ethically in the 21st century.

### Mentorship and Guidance
One of the highlights of the seminar was the interactive panel session, where young leaders shared their personal journeys, struggles, and breakthroughs. Mentors offered guidance on navigating systemic challenges, resolving conflicts constructively, and staying true to one's values in difficult times.

### Empowering the Next Generation
Ethical leadership must be nurtured early. Through group simulations and case studies, participants practiced collaborative decision-making and project planning. We believe that by investing in the character and skills of these young leaders, we are shaping a more just and prosperous future.""",
        "image": "blogs/youth3.jpeg",
        "image_description": "A panel discussion with young leaders sharing their leadership journeys.",
        "event_description": "Annual Leadership Conference - June 2026",
    },
    {
        "id": 5,
        "title": "Environmental Advocacy and Climate Action",
        "slug": "environmental-advocacy-and-climate-action",
        "author": "Pink Cycle Team",
        "content": """### Protecting Our Planet
Climate change is no longer a distant threat; it is an active crisis affecting our communities, agriculture, and water sources. The Green Earth Initiative brought together environmental activists and community volunteers to discuss local climate adaptation strategies and organize direct conservation action.

### Hands-on Conservation
The highlight of the event was a massive tree-planting drive in a degraded local forest area. Over 500 indigenous tree seedlings were planted, which will help restore the local canopy, prevent soil erosion, and support native wildlife. Volunteers also learned about proper tree care to ensure high survival rates.

### Advocacy and Education
Alongside the planting, we conducted an advocacy workshop focused on policy awareness and eco-friendly daily choices. From reducing single-use plastics to conserving water and energy at home, every small action counts. Empowering individuals to advocate for environmental policy is key to systemic change.""",
        "image": "blogs/youth4.jpeg",
        "image_description": "Volunteers planting trees in a degraded forest area.",
        "event_description": "Green Earth Initiative - June 2026",
    },
    {
        "id": 6,
        "title": "Entrepreneurship: Turning Ideas into Reality",
        "slug": "entrepreneurship-turning-ideas-into-reality",
        "author": "Pink Cycle Team",
        "content": """### The Spirit of Innovation
Startups and small businesses are the heartbeat of the economy, driving innovation and creating valuable jobs. Our Innovation Hub Pitch Day was designed to give young, aspiring entrepreneurs the platform and tools they need to turn their business concepts into sustainable enterprises.

### Pitching to Success
The event featured a pitching contest where finalists presented their business models to a panel of experienced investors and business mentors. From sustainable fashion to agritech solutions, the ideas showcased the brilliant creativity of the youth. Winners received seed funding and direct mentorship opportunities.

### Building Business Acumen
In addition to the pitches, we held masterclasses on business planning, financial literacy, and marketing strategies. We aim to equip young entrepreneurs not just with capital, but with the critical knowledge and networks required to navigate the competitive business landscape successfully.""",
        "image": "blogs/youth5.jpeg",
        "image_description": "An entrepreneur pitching their business idea to a panel of investors.",
        "event_description": "Innovation Hub Pitch Day - June 2026",
    },
    {
        "id": 7,
        "title": "Art and Culture: Expressing Identity",
        "slug": "art-and-culture-expressing-identity",
        "author": "Pink Cycle Team",
        "content": """### Creativity Unbound
Art is more than just aesthetics; it is a powerful medium for self-expression, storytelling, and social change. The Youth Arts Festival was a celebration of cultural diversity, showcasing the immense creative talents of local painters, sculptors, musicians, and poets.

### Art as a Catalyst for Change
Many of the artworks displayed addressed pressing social issues, such as gender equality, environmental preservation, and mental health awareness. The live poetry and music performances captivated the audience, proving that creative expressions can spark critical conversations and build empathy.

### Supporting Creative Talents
Providing platforms for young artists is essential for preserving our cultural heritage and fostering economic opportunities in the creative sector. Workshops on portfolio building and digital art marketing helped participants learn how to monetize their talents while staying true to their artistic vision.""",
        "image": "blogs/youth6.jpeg",
        "image_description": "Artists showcasing their paintings and performing live music.",
        "event_description": "Youth Arts Festival - June 2026",
    },
    {
        "id": 8,
        "title": "Sports for Social Cohesion",
        "slug": "sports-for-social-cohesion",
        "author": "Pink Cycle Team",
        "content": """### Teamwork and Discipline
Sports possess a unique power to unite people across diverse backgrounds, fostering mutual respect, teamwork, and discipline. The Unity Cup Tournament brought together youth teams from different neighborhoods to promote social cohesion and peaceful coexistence.

### Football for Peace
The regional football tournament featured high-spirited matches, where fair play and camaraderie were celebrated above all. Off the pitch, players and fans participated in workshops focused on conflict resolution, leadership, and community responsibility, showing that sports is a tool for life.

### Fostering Lifelong Bond
By creating spaces where youth can interact positively, we build social bridges that prevent conflict and crime. The tournament concluded with an awards ceremony recognizing not just the champions, but also the teams that displayed the highest level of discipline and sportsmanship.""",
        "image": "blogs/youth7.jpeg",
        "image_description": "Teams competing in a friendly football tournament.",
        "event_description": "Unity Cup Tournament - June 2026",
    },
    {
        "id": 9,
        "title": "Education: The Key to Opportunity",
        "slug": "education-the-key-to-opportunity",
        "author": "Pink Cycle Team",
        "content": """### Lifelong Learning
Education is the most powerful tool for breaking the cycle of poverty and unlocking potential. Our Back to School Drive was organized to ensure that underprivileged children have the necessary resources and encouragement to pursue their academic dreams.

### Supporting Students
Through the generosity of donors, we distributed school bags, stationery, textbooks, and hygiene kits to over 200 students. In addition, career guidance mentors held interactive sessions with older students, helping them set academic goals and explore professional pathways.

### Community Involvement
Education is a shared responsibility. We engaged parents and local teachers in discussions about creating supportive learning environments at home and school. By investing in our children's education, we are laying the foundation for a highly skilled and resilient community.""",
        "image": "blogs/youth8.jpeg",
        "image_description": "Distribution of educational materials to smiling students.",
        "event_description": "Back to School Drive - June 2026",
    },
    {
        "id": 10,
        "title": "Advocating for Human Rights",
        "slug": "advocating-for-human-rights",
        "author": "Pink Cycle Team",
        "content": """### Justice for All
Every human being deserves to live with dignity, equality, and safety. Our Human Rights Workshop aimed to educate young people about their constitutional rights, international human rights frameworks, and practical ways to advocate for themselves and others.

### Knowing Your Rights
Legal experts led interactive sessions explaining fundamental rights, including the right to education, clean water, fair labor, and freedom of expression. Participants analyzed real-world scenarios to understand how rights can be protected and what legal channels to use when violations occur.

### Creating Grassroots Advocates
Advocacy is about using your voice to defend the vulnerable. The workshop concluded with training on peaceful community mobilization, digital advocacy, and building coalitions. Equipping youth with legal knowledge empowers them to become active defenders of justice.""",
        "image": "blogs/youth9.jpeg",
        "image_description": "Participants discussing human rights principles in a classroom setting.",
        "event_description": "Human Rights Workshop - June 2026",
    }
]

db_paths = [
    "/var/www/venv/myshop/db.sqlite3",
    "/home/roy/pinkcycle/backend/db.sqlite3"
]

for db_path in db_paths:
    if os.path.exists(db_path):
        print(f"Updating database: {db_path}...")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        for blog in blogs_data:
            # Check if exists
            cursor.execute("SELECT id FROM shop_blog WHERE id = ?", (blog["id"],))
            row = cursor.fetchone()
            if row:
                # Update
                cursor.execute(
                    "UPDATE shop_blog SET title=?, slug=?, author=?, content=?, image=?, image_description=?, event_description=? WHERE id=?",
                    (blog["title"], blog["slug"], blog["author"], blog["content"], blog["image"], blog["image_description"], blog["event_description"], blog["id"])
                )
            else:
                # Insert
                cursor.execute(
                    "INSERT INTO shop_blog (id, title, slug, author, content, image, image_description, event_description, created) VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))",
                    (blog["id"], blog["title"], blog["slug"], blog["author"], blog["content"], blog["image"], blog["image_description"], blog["event_description"])
                )
        conn.commit()
        conn.close()
        print(f"Database {db_path} updated successfully.")
    else:
        print(f"Path does not exist: {db_path}")

print("All blogs contents updated successfully.")
