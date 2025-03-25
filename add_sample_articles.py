import os
import sys
import django
from django.utils.text import slugify
from django.utils import timezone
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dsmtimes.settings')
django.setup()

from core.models import Article, Category, User, Tag

def add_sample_articles():
    try:
        # Get or create a user
        user, created = User.objects.get_or_create(
            username='admin',
            defaults={'password': 'adminpass', 'is_active': True}
        )
        if created:
            user.set_password('adminpass')  # Set a secure password
            user.save()
            logger.info("Created new user 'admin'")
        else:
            logger.info("Using existing user 'admin'")

        # Create categories if they don’t exist
        categories = {
            'Technology': Category.objects.get_or_create(name='Technology', slug=slugify('Technology'))[0],
            'Science': Category.objects.get_or_create(name='Science', slug=slugify('Science'))[0],
            'Culture': Category.objects.get_or_create(name='Culture', slug=slugify('Culture'))[0],
        }
        logger.info("Categories ensured: Technology, Science, Culture")

        # Sample articles data
        articles = [
            {
                'title': 'The AI Revolution: Transforming Industries in 2025',
                'summary': 'Explore how artificial intelligence is reshaping healthcare, finance, and more this year.',
                'content': 'Artificial intelligence continues to evolve, with breakthroughs in natural language processing and machine learning driving innovation across industries...',
                'category': categories['Technology'],
                'is_premium': False,
                'tags': ['AI', 'Innovation'],
            },
            {
                'title': 'Quantum Computing: The Next Frontier Unveiled',
                'summary': 'Quantum computers promise unprecedented power—here’s what’s happening in 2025.',
                'content': 'In 2025, quantum computing is no longer a distant dream. Companies like IBM and Google are pushing the boundaries...',
                'category': categories['Technology'],
                'is_premium': True,
                'tags': ['Quantum', 'Tech'],
            },
            {
                'title': 'Mars Colonization: SpaceX’s Bold 2030 Plan',
                'summary': 'Elon Musk’s vision for Mars takes shape with new timelines and tech.',
                'content': 'SpaceX has updated its roadmap for Mars colonization, targeting a crewed mission by 2030...',
                'category': categories['Science'],
                'is_premium': False,
                'tags': ['Space', 'Mars'],
            },
            {
                'title': 'The Rise of Digital Art: NFTs Beyond the Hype',
                'summary': 'How digital art is finding new life in a post-NFT world.',
                'content': 'Non-fungible tokens sparked a revolution, but the real story is how artists are now leveraging blockchain...',
                'category': categories['Culture'],
                'is_premium': False,
                'tags': ['Art', 'NFTs'],
            },
            {
                'title': 'Climate Tech: Can Innovation Save the Planet?',
                'summary': 'A look at the startups racing to reverse climate change.',
                'content': 'From carbon capture to renewable energy, climate tech startups are at the forefront of the fight against global warming...',
                'category': categories['Science'],
                'is_premium': True,
                'tags': ['Climate', 'Tech'],
            },
            {
                'title': 'The Metaverse in 2025: Reality or Mirage?',
                'summary': 'The metaverse promised a new digital frontier—where are we now?',
                'content': 'Once hailed as the future, the metaverse has faced setbacks, but new VR and AR advancements suggest...',
                'category': categories['Technology'],
                'is_premium': False,
                'tags': ['Metaverse', 'VR'],
            },
            {
                'title': 'Gene Editing: CRISPR’s Next Big Leap',
                'summary': 'CRISPR technology is advancing—here’s what it means for humanity.',
                'content': 'Gene editing with CRISPR is moving beyond the lab, with applications in medicine and agriculture...',
                'category': categories['Science'],
                'is_premium': False,
                'tags': ['CRISPR', 'Biology'],
            },
            {
                'title': 'The Streaming Wars: Who’s Winning in 2025?',
                'summary': 'Netflix, Disney, and new players battle for dominance in the streaming market.',
                'content': 'The streaming landscape has evolved, with AI-driven content recommendations and exclusive releases...',
                'category': categories['Culture'],
                'is_premium': True,
                'tags': ['Streaming', 'Media'],
            },
            {
                'title': 'Cybersecurity in the Age of AI Hackers',
                'summary': 'AI-powered cyberattacks are rising—how can we stay safe?',
                'content': 'As artificial intelligence enhances hacking tools, cybersecurity experts are racing to adapt...',
                'category': categories['Technology'],
                'is_premium': False,
                'tags': ['Cybersecurity', 'AI'],
            },
            {
                'title': 'The Future of Work: Remote, Hybrid, or Back to the Office?',
                'summary': 'How work models are shifting in 2025 and beyond.',
                'content': 'The pandemic reshaped work, but 2025 brings new debates about productivity and culture...',
                'category': categories['Culture'],
                'is_premium': False,
                'tags': ['Work', 'Remote'],
            },
            {
                'title': 'Fusion Energy: Closer Than Ever?',
                'summary': 'Breakthroughs in fusion energy could change the world—here’s the latest.',
                'content': 'Scientists report progress in fusion reactors, promising a clean energy future...',
                'category': categories['Science'],
                'is_premium': True,
                'tags': ['Energy', 'Fusion'],
            },
            {
                'title': 'Smart Cities: Urban Living Reimagined',
                'summary': 'How technology is transforming cities in 2025.',
                'content': 'From IoT sensors to autonomous transport, smart cities are becoming reality...',
                'category': categories['Technology'],
                'is_premium': False,
                'tags': ['Smart Cities', 'IoT'],
            },
            {
                'title': 'The Space Tourism Boom: Tickets to the Stars',
                'summary': 'Space tourism takes off—literally—in 2025.',
                'content': 'Companies like Blue Origin and Virgin Galactic are making space travel accessible...',
                'category': categories['Science'],
                'is_premium': False,
                'tags': ['Space', 'Tourism'],
            },
            {
                'title': 'Virtual Influencers: The Rise of Digital Celebrities',
                'summary': 'Meet the AI-generated stars dominating social media.',
                'content': 'Virtual influencers like Lil Miquela are blurring the lines between reality and fiction...',
                'category': categories['Culture'],
                'is_premium': True,
                'tags': ['AI', 'Social Media'],
            },
            {
                'title': 'Blockchain Beyond Crypto: Real-World Uses',
                'summary': 'Blockchain technology is finding new applications in 2025.',
                'content': 'Beyond Bitcoin, blockchain is revolutionizing supply chains, voting, and more...',
                'category': categories['Technology'],
                'is_premium': False,
                'tags': ['Blockchain', 'Tech'],
            },
            {
                'title': 'The Brain-Computer Interface Race',
                'summary': 'Neuralink and others are connecting minds to machines.',
                'content': 'Brain-computer interfaces are advancing, with potential to treat disorders and enhance cognition...',
                'category': categories['Science'],
                'is_premium': True,
                'tags': ['BCI', 'Neuralink'],
            },
            {
                'title': 'Gaming in 2025: The Next Level',
                'summary': 'How gaming is evolving with VR, AI, and cloud tech.',
                'content': 'The gaming industry is pushing boundaries with immersive experiences and new platforms...',
                'category': categories['Culture'],
                'is_premium': False,
                'tags': ['Gaming', 'VR'],
            },
            {
                'title': 'The Electric Vehicle Surge: Roads Go Green',
                'summary': 'EVs dominate in 2025—here’s why.',
                'content': 'Electric vehicles are everywhere, thanks to better batteries and charging infrastructure...',
                'category': categories['Technology'],
                'is_premium': False,
                'tags': ['EV', 'Green Tech'],
            },
            {
                'title': 'Synthetic Biology: Engineering Life Itself',
                'summary': 'Scientists are rewriting the rules of biology—what’s next?',
                'content': 'Synthetic biology is creating new organisms, with applications from medicine to fuel...',
                'category': categories['Science'],
                'is_premium': True,
                'tags': ['Biology', 'Tech'],
            },
            {
                'title': 'The Podcast Renaissance: Audio’s Golden Age',
                'summary': 'Why podcasts are bigger than ever in 2025.',
                'content': 'Podcasts have evolved with AI hosts and interactive formats, captivating global audiences...',
                'category': categories['Culture'],
                'is_premium': False,
                'tags': ['Podcasts', 'Media'],
            },
        ]

        # Insert articles into the database
        for article_data in articles:
            article, created = Article.objects.get_or_create(
                title=article_data['title'],
                defaults={
                    'slug': slugify(article_data['title']),
                    'author': user,
                    'category': article_data['category'],
                    'content': article_data['content'],
                    'summary': article_data['summary'],
                    'is_premium': article_data['is_premium'],
                    'status': 'published',
                    'published_at': timezone.now(),
                    # 'featured_image': 'article_images/sample.jpg'  # Uncomment and set a valid path if you have images
                }
            )
            if created:
                for tag_name in article_data['tags']:
                    tag, _ = Tag.objects.get_or_create(name=tag_name.strip(), slug=slugify(tag_name))
                    article.tags.add(tag)
                logger.info(f"Added article: {article_data['title']}")
            else:
                logger.info(f"Article already exists: {article_data['title']}")

        logger.info("Successfully added 20 sample articles!")

    except Exception as e:
        logger.error(f"Error adding sample articles: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    add_sample_articles()