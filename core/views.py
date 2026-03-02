import os
import json
import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django import forms
from django.forms import ModelForm

# Import your models (Unified)
from .models import (
    Testimonial, UploadedFile, ContactMessage, 
    Post, Comment, ProgramRegistration
)
from .forms import ContactForm
from .services.email_service import send_admin_notification, send_user_confirmation
# A simple form for comments (add this to forms.py later if you want)
# For now, we'll define it here for simplicity in views.py
class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ('content',)
        widgets = {
            # THIS IS THE CORRECTED LINE:
            # We use forms.Textarea because we are defining a widget for the form,
            # not a field type for the model.
            'content': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Write your comment here...'}),
        }



# --- GLOBAL DATA FOR SERVICES AND PROJECTS ---
# These dictionaries should be defined once at the module level (top of the file)
# so they are created when Django loads the file and can be accessed by all views.
services_data = {
    'web-mobile-backend': {
        'title': 'Full-Stack Web & Mobile Development',
        'description': 'End-to-end digital solutions. We combine sleek frontend interfaces with robust backend architectures. Whether it is a RESTful API, a database-driven web app, or a native Android APK, we build for performance and security.',
        'image_url': 'core/images/services/fullstack_dev.jpg',
        'tools_stack': ['React.js', 'Next.js', 'Python (Django)', 'Node.js', 'PostgreSQL', 'Capacitor', 'AWS'],
        'benefits': [
            'Robust Backend: Secure data handling and server-side logic.',
            'Mobile Ready: Native Android APKs from the same codebase.',
            'Fast Performance: Optimized for speed and low latency.',
            'Scalable: Built to handle growing user bases.'
        ],
        'how_we_work': [
            'Requirement gathering and system architecture design.',
            'Backend API development and Database schema setup.',
            'Frontend UI implementation and Mobile APK conversion.',
            'Deployment to cloud servers and final QA testing.'
        ]
    },
    'top-notch-graphics': {
        'title': 'High-Fidelity Graphics & Media',
        'description': 'Premium visual branding designed to make your business stand out. We specialize in tech-studio aesthetics—minimalist, modern, and high-impact designs.',
        'image_url': 'core/images/services/graphics.jpg',
        'tools_stack': ['Adobe Photoshop', 'Illustrator', 'CorelDRAW', 'Figma', 'Canva Pro'],
        'benefits': [
            'Professional Logos: Distinctive and memorable brand marks.',
            'Marketing Assets: High-conversion flyers and social kits.',
            'UI Assets: Custom icons and visual components.',
            'Print Ready: High-resolution files for banners.'
        ],
        'how_we_work': [
            'Brand discovery and mood-board creation.',
            'Concept sketching and digital drafting.',
            'Iterative feedback and color theory refinement.',
            'Final delivery of source files and export formats.'
        ]
    },
    'seo-content-strategy': {
        'title': 'SEO & Content Drafting',
        'description': 'Visibility is currency. We draft SEO-optimized content that ranks on search engines and speaks to your audience.',
        'image_url': 'core/images/services/seo_content.jpg',
        'tools_stack': ['Google Analytics', 'SEMrush', 'Grammarly Business', 'WordPress SEO'],
        'benefits': [
            'Higher Rankings: Targeted keywords for organic growth.',
            'Professional Tone: Well-crafted content building authority.',
            'Technical Writing: Clear guides and descriptions.',
            'Engagement: Turning visitors into leads.'
        ],
        'how_we_work': [
            'Keyword research and competitor gap analysis.',
            'Content drafting with a focus on SEO best practices.',
            'On-page optimization and readability checks.',
            'Publishing and performance tracking via Analytics.'
        ]
    },
    'tech-skills-siwes': {
        'title': 'Tech Skills & SIWES Training',
        'description': 'Hands-on mentorship for the next generation of innovators. Project-based training and SIWES support for students.',
        'image_url': 'core/images/services/training.jpg',
        'tools_stack': ['Python', 'Web Dev', 'SPSS', 'Technical Reporting'],
        'benefits': [
            'Industry Experience: Work on live studio projects.',
            'Logbook Support: Guidance on IT documentation.',
            'Skill Acquisition: Master in-demand programming.',
            'Defense Prep: Mock presentations for students.'
        ],
        'how_we_work': [
            'Assessment of current skill level and goal setting.',
            'Structured curriculum with daily practical tasks.',
            'Bi-weekly project reviews and logbook vetting.',
            'Final project completion and defense preparation.'
        ]
    },
    'virtual-assistance-email': {
        'title': 'Virtual Assistance & Email Marketing',
        'description': 'Offload your administrative burden. We handle professional communication and automated email campaigns.',
        'image_url': 'core/images/services/va_email.jpg',
        'tools_stack': ['Mailchimp', 'Google Workspace', 'Calendly', 'Slack'],
        'benefits': [
            'Automation: Set-and-forget email sequences.',
            'Organization: Clean inbox and managed schedules.',
            'Communication: Professional client responses.',
            'Efficiency: Focus on your core business.'
        ],
        'how_we_work': [
            'Workflow audit to identify repetitive tasks.',
            'Setup of scheduling and communication tools.',
            'Execution of admin tasks or email campaign drafts.',
            'Monthly reporting on efficiency and engagement.'
        ]
    },
    'it-support-technical': {
        'title': 'IT Support & Technical Assistance',
        'description': 'Troubleshooting, system administration, and network optimization to ensure your infrastructure remains operational.',
        'image_url': 'core/images/services/it_support.jpg',
        'tools_stack': ['Windows/Linux', 'Networking', 'Remote Desk', 'Hardware Diagnostics'],
        'benefits': [
            'Zero Downtime: Rapid response to glitches.',
            'System Security: Protection against malware.',
            'Network Setup: Optimized office Wi-Fi/LAN.',
            'Device Health: Proactive maintenance.'
        ],
        'how_we_work': [
            'Full infrastructure audit and vulnerability scan.',
            'Implementation of maintenance and security protocols.',
            'Ongoing remote support and on-site visits.',
            'Quarterly performance and health reports.'
        ]
    },
    'data-analysis-research': {
        'title': 'Data Analysis & Research Support',
        'description': 'Turning complex data into actionable insights. Statistical analysis and research support for businesses.',
        'image_url': 'core/images/services/data_analysis.jpg',
        'tools_stack': ['SPSS', 'Advanced Excel', 'SQL', 'Python (Pandas)'],
        'benefits': [
            'Accurate Reporting: Error-free statistical results.',
            'Visual Insights: Clear charts and visualizations.',
            'Research Validity: Methodologically sound analysis.',
            'Automation: Automated Excel reporting.'
        ],
        'how_we_work': [
            'Data cleaning and hypothesis formulation.',
            'Running statistical tests (SPSS/SQL/Python).',
            'Interpretation of results and chart generation.',
            'Delivery of a comprehensive research report.'
        ]
    },
    'general-contract-supplies': {
        'title': 'General Contract & Technical Supplies',
        'description': 'As **Usty Alhaji Service Enterprise**, we handle general contracts and the supply of specialized technical equipment.',
        'image_url': 'core/images/services/contract.jpg',
        'tools_stack': ['Hardware Procurement', 'Logistics', 'Supply Chain'],
        'benefits': [
            'Quality Sourcing: Genuine tech hardware.',
            'Reliability: Timely delivery of requirements.',
            'Technical Expertise: We know the specs.',
            'Compliance: Registered for tenders.'
        ],
        'how_we_work': [
            'Quotation request and specification vetting.',
            'Source procurement from verified vendors.',
            'Quality control and logistics planning.',
            'Secure delivery and installation at client site.'
        ]
    },
    'academic-support-writing': {
        'title': 'Academic Support & SIWES Logs',
        'description': 'Specialized support for IT students. We assist with technical writing and project defense preparation.',
        'image_url': 'core/images/services/academic.jpg',
        'tools_stack': ['Technical Writing', 'Logbook Documentation', 'Presentation'],
        'benefits': [
            'Grade Improvement: High-quality output.',
            'Clarity: Simple explanations of tech concepts.',
            'Structure: Professionally formatted reports.',
            'Confidence: Ready for external supervisors.'
        ],
        'how_we_work': [
            'Review of project topics and logbook guidelines.',
            'Drafting technical chapters and documentation.',
            'Reviewing for plagiarism and technical accuracy.',
            'Final polishing and presentation coaching.'
        ]
    }
}
projects_data = {
    'jira-task-engine': {
        'title': 'High-Velocity Engineering: Async Jira Task Engine & TDD Suite',
        'tagline': 'A high-performance backend core built with Python 3.12+, FastAPI, and Pydantic V2.',
        'client_type': 'Internal Tooling / Enterprise Backend',
        'category': 'others',
        'thumbnail': 'projects/backend_preview.jpg',
        'overview': (
            "The 'High-Velocity Jira Task Engine' is a technical demonstration of modern backend engineering principles, focusing on high-performance concurrency and data integrity. "
            "Built using Python 3.12+, this engine utilizes Asynchronous IO (asyncio) to handle multiple task creations and status updates concurrently, simulating a high-traffic enterprise environment. "
            "The system leverages Pydantic V2 for strict data validation, ensuring that every task entering the system meets rigorous schema requirements before reaching the database layer. "
            "A core highlight of this project is the integrated Test-Driven Development (TDD) suite. This suite automatically verifies system reliability by running concurrent test engines that simulate real-world stress, "
            "ensuring 100% uptime and zero-error data processing. The modular architecture allows for easy integration with PostgreSQL or MongoDB, making it a scalable solution for modern software teams."
        ),
        'technologies': [
            'Python 3.12', 'FastAPI', 'Pydantic V2', 'Asyncio', 
            'Pytest', 'TDD', 'REST API', 'JSON Schema', 
            'UUID4', 'NumPy'
        ],
        'expertise': [
            'Developing high-performance asynchronous systems using Python 3.12 and asyncio for non-blocking execution.',
            'Implementing strict data modeling and schema validation using Pydantic V2 field validators.',
            'Applying Test-Driven Development (TDD) methodologies to build a self-verifying software architecture.',
            'Utilizing UUID4 and Python Enum classes to ensure unique data identification and consistent state management.',
            'Designing modular service layers that separate business logic from data storage for maximum scalability.',
            'Simulating high-velocity concurrent environments to test system stability under heavy data loads.'
        ],
        'features': [
            'Asynchronous Task Engine capable of handling concurrent creation requests without performance lag.',
            'Automated TDD Test Suite with terminal output verification and status reporting.',
            'Pydantic-powered validation layer that prevents empty titles or invalid status transitions.',
            'Real-time status tracking (To Do, In Progress, Done) with automated timestamps.',
            'Scalable architecture designed for easy conversion into a full REST API with FastAPI.',
            'Modular JiraService class that supports future database migrations (SQL/NoSQL).'
        ],
        'screenshots': [
            'jira1.png', 'jira2.png', 'jira3.png','jira4.png'
        ],

        'github_link': 'https://github.com/UASE-TECH-STUDIO/Jira-Gmail-Velocity-Engine.git',
        'problem_solution': {
            'problem': 'Enterprise systems often struggle with data consistency and performance bottlenecks when handling high volumes of concurrent status updates and task creation.',
            'solution': 'Developed a modular, asynchronous engine using Python 3.12+ that utilizes non-blocking IO and Pydantic V2 validation. This ensures data integrity at the entry point and allows the system to scale horizontally with 100% reliability verified through TDD.'
        },
        'downloads': [],
    },
    'recipe-management-app': {
    'title': 'Smart Recipe Management Application',
    'tagline': 'A feature-rich platform for creating, managing, and discovering recipes.',
    'client_type': 'Food Creators / Home Cooks / Restaurants',
    'category': 'web-apps',
    'thumbnail': 'projects/recipe_app_thumbnail.jpg',
    'overview': (
        'The Smart Recipe Management Application is a full-stack web platform designed to help users '
        'create, organize, and discover cooking recipes in a structured and visually engaging way. '
        'Users can add detailed recipes including ingredients, step-by-step cooking instructions, '
        'images, and optional video references. Recipes can be categorized, searched, and filtered '
        'to improve discoverability and user experience.\n\n'
        'The system includes a robust administrative backend for managing recipe content, moderating '
        'user submissions, and organizing categories. Its responsive design ensures seamless usage '
        'across desktop, tablet, and mobile devices, making it suitable for both personal and '
        'professional culinary use.'
    ),
    'technologies': [
        'Next.js', 'React.js', 'TypeScript', 'Tailwind CSS',
        'Node.js', 'Express.js', 'MongoDB', 'Mongoose'
    ],
    'expertise': [
        'Designing scalable RESTful APIs for recipe and category management.',
        'Implementing dynamic frontend interfaces with React and Tailwind CSS.',
        'Structuring flexible MongoDB schemas for ingredients, steps, and media assets.',
        'Handling file uploads and media presentation securely.',
        'Building responsive and accessible UI components.'
    ],
    'features': [
        'Create, edit, and delete recipes',
        'Ingredient lists with measurements',
        'Step-by-step cooking instructions',
        'Recipe images and optional video links',
        'Search, filter, and category-based discovery',
        'Admin moderation and content control',
        'Fully responsive user interface'
    ],
    'screenshots': [
        'recipe0.jpg', 'recipe1.jpg', 'recipe2.jpg', 'recipe3.jpg', 'recipe4.jpg', 'recipe5.jpg', 'recipe6.jpg',
        'recipe7.jpg', 'recipe8.jpg', 'recipe9.jpg' 'recipe10.jpg', 'recipe11.jpg', 'recipe12.jpg', 'recipe13.jpg',
        'recipe14.jpg', 'recipe15.jpg', 'recipe16.jpg', 'recipe17.jpg', 'recipe18.jpg', 'recipe19.jpg'
    ],
    'live_demo_link': 'https://recipes-one-alpha.vercel.app/',
    'github_link': 'https://github.com/UASE-TECH-STUDIO',
    'problem_solution': {
        'problem': 'Many recipe platforms are cluttered, difficult to manage, or lack structured content organization.',
        'solution': 'This application provides a clean, structured, and scalable recipe management system with intuitive navigation and powerful content organization.'
    },
    'downloads': [],
},

'blood-donor-management-system': {
    'title': 'Blood Donor Management System',
    'tagline': 'Connecting blood donors, recipients, and healthcare institutions efficiently.',
    'client_type': 'Healthcare / NGOs / Blood Banks',
    'category': 'web-apps',
    'thumbnail': 'projects/blood_donor_thumbnail.jpg',
    'overview': (
        'The Blood Donor Management System is a life-impacting web application designed to bridge the gap '
        'between blood donors, beneficiaries, and healthcare institutions. Donors can register their '
        'blood groups and availability, while beneficiaries can submit blood requests during emergencies.\n\n'
        'Administrators have full control over donor verification, request approvals, and request tracking. '
        'The system improves response time during critical situations and ensures transparency in blood '
        'donation processes.'
    ),
    'technologies': [
        'Next.js', 'React.js', 'TypeScript', 'Tailwind CSS',
        'Node.js', 'MongoDB', 'Mongoose'
    ],
    'expertise': [
        'Designing multi-role systems (donor, beneficiary, admin).',
        'Implementing request approval workflows.',
        'Secure handling of sensitive health-related data.',
        'Building scalable dashboards for real-time monitoring.'
    ],
    'features': [
        'Donor registration and profile management',
        'Blood request submission and tracking',
        'Admin approval and rejection workflows',
        'Request status updates',
        'Role-based access control',
        'Responsive dashboard interfaces'
    ],
    'screenshots': [
        'blood0.jpg', 'blood1.jpg', 'blood2.jpg', 'blood3.jpg', 'blood4.jpg', 'blood5.jpg', 'blood6.jpg',
        'blood7.jpg', 'blood8.jpg', 'blood9.jpg', 'blood10.jpg', 'blood11.jpg','blood12.jpg', 'blood13.jpg',
        'blood14.jpg', 'blood15.jpg', 'blood16.jpg', 'blood17.jpg', 'blood18.jpg', 'blood19.jpg', 'blood20.jpg',
        'blood21.jpg', 'blood22.jpg',
    ],
    'live_demo_link': 'https://blood-donor-app-pied.vercel.app/',
    'github_link': 'https://github.com/UASE-TECH-STUDIO',
    'problem_solution': {
        'problem': 'Blood shortages and delayed donor discovery during emergencies.',
        'solution': 'The system enables fast donor identification and streamlined blood request handling.'
    },
    'downloads': [],
},


    'food-ordering-app': {
        'title': 'Deliciously Simple: The Food Ordering Application (Web + Android APK)',
        'tagline': 'A full-stack food ordering platform with web and native Android APK access.',
        'client_type': 'Restaurant / Food Delivery Startup',
        'category': 'mobile-apps',
        'thumbnail': 'projects/food_thumbnail.jpg',
        'overview': (
            "The 'Deliciously Simple' Food Ordering Application is a comprehensive digital platform designed to revolutionize how customers order and manage their favorite meals. "
            "This full-stack solution, accessible via both a modern web interface and a native Android APK, empowers users to browse menus, customize orders, and make secure payments from the comfort of their homes. "
            "Customers can track their orders in real-time, view their complete order history, and even request modifications or cancellations (within defined parameters). "
            "For restaurant management, the application provides a powerful backend system to effortlessly edit and add menu items, control inventory, and manage user accounts. A standout feature is the integrated live chat system, allowing management to communicate directly with customers. "
            "This includes a pre-programmed bot for instant first replies, ensuring immediate customer engagement until a human representative takes over. "
            "Management can also efficiently oversee order fulfillment, adjust delivery times, and update order statuses, with all changes instantly reflected on the customer's order history page. "
            "Furthermore, the system includes robust user management capabilities, enabling administrators to edit user details upon request, block or delete users for policy violations, and control overall user access. "
            "A built-in newsletter subscription feature allows customers to opt-in for exclusive discounts and updates, fostering loyalty and driving repeat business. "
            "This application represents a seamless, intuitive, and feature-rich experience for both diners and food service providers."
        ),
        'technologies': [
            'React.js', 'Next.js', 'TypeScript', 'Tailwind CSS',
            'Node.js', 'Express.js', 'MongoDB', 'Capacitor',
            'Axios', 'Stripe API'
        ],
        'expertise': [
            'Building a scalable React & Next.js frontend with responsive Tailwind CSS styling for a modern, engaging UI.',
            'Managing complex state using React Hooks and Context API for seamless user interactions and efficient data flow.',
            'Designing and implementing robust RESTful APIs in Node.js and integrating MongoDB for flexible, schema-less data storage tailored for dynamic food menus and orders.',
            'Implementing secure payment processing with Stripe API integration for real-time, multi-option credit card payments and efficient checkout flows.',
            'Developing comprehensive user management with secure authentication, profile management, and role-based access control.',
            'Creating an advanced order management system with real-time updates for both customers and restaurant administrators.',
            'Implementing dynamic menu management functionalities for administrators (add/update/delete dishes, categories, and pricing).',
            'Utilizing Capacitor for mobile app packaging and deployment, converting the web application into a native Android APK with equivalent features and smooth performance, enabling offline support and native mobile functionalities.'
        ],
        'features': [
            'User-friendly interface to browse menus, add items to cart, and place orders efficiently.',
            'Dedicated Admin panel with comprehensive order management, menu management (add/edit/delete items), and user management controls.',
            'Secure payment and checkout flow seamlessly integrated with Stripe.',
            'Fully responsive design for optimal viewing and interaction on desktop and mobile browsers.',
            'Native Android APK app offering equivalent features and a smooth, integrated mobile experience.',
            'Real-time order tracking and status updates for customers.',
            'User profile management and order history.'
        ],
        'screenshots': [
            'food_ordering_app_screenshot_1.jpg', 'food_ordering_app_screenshot_2.jpg', 'food_ordering_app_screenshot_3.jpg',
            'food_ordering_app_screenshot_4.jpg', 'food_ordering_app_screenshot_5.jpg', 'food_ordering_app_screenshot_6.jpg',
            'food_ordering_app_screenshot_7.jpg', 'food_ordering_app_screenshot_8.jpg', 
           
        ],
        'live_demo_link': 'https://unilag-foodapp.vercel.app/',
        'github_link': 'https://github.com/UASE-TECH-STUDIO',
        'problem_solution': {
            'problem': 'Many restaurants lacked a modern, efficient, and mobile-friendly way for customers to order food online, leading to missed sales and customer inconvenience, especially on mobile devices.',
            'solution': 'Developed a user-friendly web and native Android application that provides a smooth ordering experience, secure payments via Stripe, and real-time tracking. The use of React/Next.js and Capacitor ensured a high-performance, cross-platform solution, enhancing customer satisfaction and boosting restaurant sales.'
        },
        'downloads': [{'name': 'Download Android APK', 'file_url': ''}],
    },

 'campus-food-delivery-app': {
    'title': 'UNILAGEats: Campus Food Delivery Application (Web + Android APK)',
    'tagline': 'A campus-focused food ordering and delivery platform designed exclusively for university communities.',
    'client_type': 'Universities / Campus Food Vendors / Student Communities',
    'category': 'mobile-apps',
    'thumbnail': 'projects/campus_food_thumbnail.jpeg',
    'overview': (
        'UNILAGEats is a comprehensive campus food delivery application specifically designed to serve '
        'university environments, where traditional city-wide food delivery platforms often fall short. '
        'The platform provides students with a seamless way to order meals from approved on-campus food '
        'vendors, cafeterias, and food courts using both a modern web interface and a native Android APK.\n\n'
        'Students can browse vendor menus, customize their orders, and place requests securely within '
        'the campus ecosystem. Orders are tracked in real time, allowing users to monitor preparation '
        'and delivery progress without leaving the application. The platform enforces campus-based '
        'restrictions, ensuring that only verified students and authorized vendors can access services.\n\n'
        'For vendors and administrators, UNILAGEats offers a powerful backend system for managing menus, '
        'orders, availability, and delivery workflows. Administrators can onboard vendors, manage user '
        'accounts, monitor transactions, and oversee platform activity. The Android APK version ensures '
        'smooth mobile performance, offline resilience for limited connectivity scenarios, and native '
        'device integration tailored to student usage patterns.'
    ),
    'technologies': [
        'React.js', 'Next.js', 'TypeScript', 'Tailwind CSS',
        'Node.js', 'Express.js', 'MongoDB', 'Capacitor',
        'Axios', 'Payment Gateway Integration'
    ],
    'expertise': [
        'Designing campus-restricted multi-vendor food delivery architectures.',
        'Building scalable React and Next.js frontends optimized for student usage and mobile responsiveness.',
        'Managing application state efficiently using modern React patterns for smooth ordering flows.',
        'Developing secure RESTful APIs with Node.js and Express for order, vendor, and user management.',
        'Structuring MongoDB schemas for vendors, menus, campus zones, and delivery tracking.',
        'Packaging and deploying the web application as a native Android APK using Capacitor.',
        'Implementing role-based access control for students, vendors, and administrators.',
        'Optimizing performance for low-bandwidth campus network environments.'
    ],
    'features': [
        'Student authentication and campus-based user verification',
        'Multi-vendor campus food listings and categorized menus',
        'Meal customization and cart-based ordering system',
        'Real-time order tracking and status updates',
        'Vendor dashboard for managing menus and incoming orders',
        'Administrative panel for vendor onboarding and system oversight',
        'Fully responsive web interface for desktop and mobile browsers',
        'Native Android APK with equivalent features and smooth performance',
        'Order history and user profile management'
    ],
     'screenshots': [
            'unilag-food-app1.jpeg', 'unilag-food-app2.jpeg', 'unilag-food-app3.jpeg',
            'unilag-food-app4.jpeg', 'unilag-food-app5.jpeg', 'unilag-food-app6.jpeg',
            'unilag-food-app7.jpeg', 'unilag-food-app8.jpeg', 'unilag-food-app9.jpeg',
            'unilag-food-app10.jpeg', 'unilag-food-app11.jpeg', 'unilag-food-app12.jpeg',
        ],
    'live_demo_link': None,
    'github_link': 'https://github.com/UASE-TECH-STUDIO',
    'problem_solution': {
        'problem': (
            'University students often struggle to access reliable food delivery services within campus '
            'environments due to location restrictions, security concerns, and lack of vendor integration. '
            'Existing city-wide food apps are not optimized for campus operations.'
        ),
        'solution': (
            'UNILAGEats was developed as a campus-first food delivery solution, providing a controlled, '
            'secure, and optimized platform that connects students directly with on-campus vendors. '
            'The system improves convenience, reduces order delays, and enhances food service accessibility '
            'within the university ecosystem.'
        )
    },
    'downloads': [
        {'name': 'Download Android APK', 'file_url': ''}
    ],
},



'film-house-cinema': {
    'title': 'Film House Cinema Booking System',
    'tagline': 'A modern cinema booking and management platform.',
    'client_type': 'Entertainment / Cinema Management',
    'category': 'web-apps',
    'thumbnail': 'projects/filmhouse_thumbnail.jpeg',
    'overview': (
        'The Film House Cinema Booking System is a full-stack web application designed to modernize '
        'movie ticket booking and cinema operations. Users can browse available movies, select showtimes, '
        'choose seats dynamically, and complete secure bookings.\n\n'
        'Administrators manage movie listings, showtimes, and customer messages via a dedicated dashboard. '
        'The system ensures smooth customer experience while simplifying cinema management workflows.'
    ),
    'technologies': [
        'Next.js 15', 'React.js', 'TypeScript',
        'Prisma ORM', 'PostgreSQL', 'NextAuth v5',
        'Tailwind CSS', 'Node.js', 'bcryptjs'
    ],
    'expertise': [
        'Implementing secure authentication with NextAuth.',
        'Dynamic seat selection logic and pricing calculation.',
        'Database modeling using Prisma ORM.',
        'Admin dashboard design and management.'
    ],
    'features': [
        'User authentication and profile management',
        'Movie listings and showtime scheduling',
        'Dynamic seat selection',
        'Admin movie and message management',
        'Secure booking workflow'
    ],
    'screenshots': [
        'film-house3.jpg', 'film-house4.jpg', 'film-house5.jpg', 'film-house6.jpg', 'film-house7.jpg',
        'film-house8.jpg', 'film-house9.jpg', 'film-house10.jpg', 'film-house11.jpg', 'film-house12.jpg',
        'film-house13.jpg'
    ],
    'live_demo_link': 'https://film-house-eight.vercel.app/',
    'github_link': 'https://github.com/Mr-Usty/film-house',
    'problem_solution': {
        'problem': 'Manual or outdated cinema booking systems reduce customer satisfaction.',
        'solution': 'The platform provides a streamlined digital booking experience with real-time seat selection.'
    },
    'downloads': [],
},

'student-clearance-system': {
    'title': 'Student Clearance Management System',
    'tagline': 'Automating academic and administrative clearance workflows.',
    'client_type': 'Universities / Polytechnics',
    'category': 'web-apps',
    'thumbnail': 'projects/clearance_thumbnail.jpg',
    'overview': (
        'The Student Clearance Management System digitizes the traditional paper-based clearance process '
        'used in higher institutions. Students submit clearance requests online, while departments '
        'review, approve, or reject requests digitally.\n\n'
        'Administrators gain full oversight of clearance progress, reducing delays, errors, and manual tracking.'
    ),
    'technologies': [
        'Next.js', 'React.js', 'TypeScript',
        'Node.js', 'MongoDB'
    ],
    'expertise': [
        'Designing multi-department approval workflows.',
        'Building role-based dashboards.',
        'Optimizing institutional process automation.'
    ],
    'features': [
        'Online clearance request submission',
        'Departmental approval stages',
        'Admin oversight and reporting',
        'Status tracking and notifications'
    ],
    'screenshots': [
        'clearance0.jpg', 'clearance1.jpg', 'clearance2.jpg', 'clearance3.jpg', 'clearance4.jpg', 'clearance5.jpg', 
        'clearance6.jpg', 'clearance7.jpg', 'clearance8.jpg',
    ],
    'live_demo_link': 'https://clearance-system-three.vercel.app/',
    'github_link': 'https://github.com/UASE-TECH-STUDIO',
    'problem_solution': {
        'problem': 'Manual clearance processes cause delays and loss of records.',
        'solution': 'The system ensures transparency, speed, and accuracy through automation.'
    },
    'downloads': [],
},

'medical-resource-procurement-system': {
    'title': 'Medical Resource Procurement System',
    'tagline': 'Streamlining medical supply sourcing and approval.',
    'client_type': 'Hospitals / Health Institutions',
    'category': 'web-apps',
    'thumbnail': 'projects/medical_procurement_thumbnail.jpeg',
    'overview': (
        'The Medical Resource Procurement System is designed to manage the sourcing, approval, and tracking '
        'of medical supplies within healthcare institutions. Departments submit procurement requests, '
        'which are reviewed and approved by authorized personnel.\n\n'
        'The platform improves accountability, inventory visibility, and operational efficiency.'
    ),
    'technologies': [
        'Next.js', 'React.js', 'TypeScript',
        'Node.js', 'MongoDB'
    ],
    'expertise': [
        'Designing approval-based procurement workflows.',
        'Inventory tracking and reporting logic.',
        'Secure handling of institutional data.'
    ],
    'features': [
        'Medical supply request management',
        'Approval workflows',
        'Vendor and inventory tracking',
        'Procurement reports'
    ],
    'screenshots': [
        'medical0.jpg', 'medical1.jpg', 'medical2.jpg', 'medical3.jpg', 'medical4.jpg', 'medical5.jpg',
    ],
    'live_demo_link': None,
    'github_link': 'https://github.com/UASE-TECH-STUDIO',
    'problem_solution': {
        'problem': 'Unstructured procurement processes cause delays and inefficiencies.',
        'solution': 'This system centralizes and automates medical resource procurement.'
    },
    'downloads': [],
},
'court-order-management-system': {
    'title': 'Court Order Management System',
    'tagline': 'Secure digital management of court orders and compliance tracking.',
    'client_type': 'Judiciary / Legal Institutions',
    'category': 'web-apps',
    'thumbnail': 'projects/court_order_thumbnail.jpeg',
    'overview': (
        'The Court Order Management System is a Django-powered web application developed to digitize '
        'the creation, issuance, and tracking of court orders. Judicial officers can issue court orders '
        'electronically, assign them to enforcement bodies, and monitor compliance status.\n\n'
        'The system ensures document integrity, auditability, and secure access to sensitive legal records, '
        'eliminating the risks associated with paper-based court documentation.'
    ),
    'technologies': [
        'Python', 'Django', 'Django ORM',
        'PostgreSQL', 'HTML5', 'CSS3',
        'JavaScript', 'Bootstrap'
    ],
    'expertise': [
        'Designing secure legal document management systems.',
        'Implementing Django-based role permissions.',
        'Audit logging and compliance tracking.',
        'Form handling and document storage.'
    ],
    'features': [
        'Digital creation and issuance of court orders',
        'Role-based access (Judges, Registrars, Enforcement)',
        'Order status tracking and compliance monitoring',
        'Secure document storage',
        'Administrative oversight dashboard'
    ],
    'screenshots': [
        'court0.jpg', 'court1.jpg', 'court2.jpg', 'court3.jpg',
    ],
    'live_demo_link': None,
    'github_link': 'https://github.com/UASE-TECH-STUDIO',
    'problem_solution': {
        'problem': 'Paper-based court order management is prone to loss, delays, and manipulation.',
        'solution': 'The system digitizes court orders with secure access and full audit trails.'
    },
    'downloads': [],
},


    'crime-tracking-system': { 
        'title': 'Crime Tracking System Web App',
        'tagline': 'A robust web-based application for efficient crime reporting and management.',
        'client_type': 'Internal Project (Prototype) / Law Enforcement / Public Sector',
        'category': 'web-apps',
        'overview': "The Crime Tracking System is a robust web-based application designed to modernize and streamline the reporting and management of criminal activities. It provides law enforcement agencies with a powerful tool to efficiently record incidents, track their status, and analyze crime patterns. This system enhances public safety by enabling faster response times and more strategic deployment of resources through real-time data and comprehensive administrative controls.",
        'technologies': ['HTML', 'CSS', 'JavaScript', 'jQuery', 'PHP', 'MySQL', 'Bootstrap', 'Figma (for UI)'],
        'thumbnail': 'projects/crime_thumbnail.jpg',
        'expertise': [
            'Building secure multi-user authentication and role-based admin access with PHP and MySQL.',
            'Implementing comprehensive CRUD operations for crime reports, alerts, and user management using PHP for backend logic.',
            'Developing dynamic UI updates with AJAX and jQuery for real-time comments, likes, and threaded replies.',
            'Designing and implementing an extensive Admin dashboard for managing crimes, comments, alerts, and administrators (including add/edit/delete functionality) with PHP.',
            'Creating an alerts and notifications system for critical crime updates.',
            'Ensuring mobile-first responsive design using the Bootstrap framework for optimal accessibility across devices.',
            'Implementing robust security features including session handling and input validation against common vulnerabilities in PHP applications.'
        ],
        'features': [
            'Detailed crime reporting with categorization, location tagging, and status tracking.',
            'Interactive comments system with likes and threaded replies to foster community interaction.',
            'Centralized Admin dashboard for alert management, user/admin control, and full CRUD operations on crimes and alerts.',
            'Secure registration and management of multiple administrative users with unique IDs.',
            'Real-time alerts and notifications for newly reported or updated crimes.',
            'Comprehensive crime viewing and detailed information display for each reported incident.',
            'Ability to view, add, edit, and delete crimes and alerts.',
        ],
        'screenshots': [
            'crime_tracking_system_screenshot_1.jpg',
            'crime_tracking_system_screenshot_2.jpg',
            'crime_tracking_system_screenshot_3.jpg',
            'crime_tracking_system_screenshot_4.jpg',
            'crime_tracking_system_screenshot_5.jpg',
            'crime_tracking_system_screenshot_6.jpg',
            'crime_tracking_system_screenshot_7.jpg',
            'crime_tracking_system_screenshot_8.jpg',
        ],
        'live_demo_link': 'http://uase-tech-studio.42web.io/index.php',
        'github_link': 'https://github.com/UASE-TECH-STUDIO',
        'problem_solution': {
            'problem': 'Many communities lack centralized platforms to report or track local criminal activity. Information is often delayed, hidden, or scattered.',
            'solution': 'We designed a simple-to-use, secure web platform using PHP and MySQL for anonymous reporting and visualization of crime data. This fosters transparency, faster response times, and community safety.'
        },
        'downloads': [
            {'name': 'PDF Project Documentation', 'file_url': 'crime_tracking_system_docs.pdf'},
            {'name': 'GitHub Source Code', 'file_url': 'https://github.com/UASE-TECH-STUDIO'},
            {'name': 'User Guide', 'file_url': 'crime_tracking_system_user_guide.pdf'},
        ],
    },
      'uase-tech-studio-website': {
        'title': 'UASE Tech Studio: Official Website & Portfolio (This Platform)',
        'tagline': 'Building a robust digital presence for UASE Tech Studio itself.',
        'client_type': 'Internal Project / Brand Showcase',
        'category': 'web-apps',
        'live_demo_link': None,
        'github_link': 'https://github.com/UASE-TECH-STUDIO',
        'thumbnail': 'projects/uase_website_thumbnail.jpg',
        'screenshots': [
            'projects/uase_website_screenshot_1.jpg',
            'projects/uase_website_screenshot_2.jpg',
            'projects/uase_website_screenshot_3.jpg',
        ],
        'overview': "This is the official online platform for UASE Tech Studio, meticulously designed and developed to serve as a comprehensive portfolio and information hub. Built with Django, this full-stack website showcases our diverse technical capabilities, featuring detailed project pages, service descriptions, and testimonials. It embodies modern UI/UX principles, ensuring responsiveness across all devices, and integrates robust backend functionalities like secure contact forms with reCAPTCHA, dynamic content management via Django Admin, and user authentication. This platform is a testament to our commitment to delivering high-quality, scalable, and secure digital solutions.",
        'technologies': ['Django', 'Python', 'HTML5', 'CSS3', 'JavaScript', 'Bootstrap 5', 'SQLite (development)', 'PostgreSQL (production ready)', 'Django Admin', 'Static File Management', 'Responsive Design', 'MS Office Suite (for content planning/documentation)', 'CorelDRAW (for logo/branding elements)'],
        'expertise': [
            'Full-stack development combining robust backend logic with modern, responsive frontend design, ensuring a seamless user experience.',
            'Comprehensive Django framework expertise: advanced URL routing, templating, powerful database ORM, and secure user authentication and authorization.',
            'Seamless Bootstrap integration for creating a highly responsive and visually appealing UI, adaptable to all screen sizes.',
            'Utilizing Python for efficient backend business logic, secure form handling, and potential API integrations.',
            'Implementing JavaScript for dynamic UI enhancements, client-side form validations, and interactive effects across the site.',
            'Strategic planning and execution for a secure user contact form with reCAPTCHA integration for spam protection and automated email notifications.',
            'Developing a comprehensive content management system (CMS) via Django Admin for easy updates of services, projects, testimonials, and other site content.',
            'Optimizing for fast loading speeds and a smooth user experience across the site.'
        ],
        'features': [
            'Modern, responsive, and innovative UI/UX design adaptable to all devices.',
            'Dynamic content management for services, projects, and testimonials via an intuitive Django Admin interface.',
            'Interactive portfolio showcasing detailed project pages with direct live demo links and GitHub repository access.',
            'Comprehensive "About Us" and "Services" sections providing in-depth information about UASE Tech Studio\'s offerings and expertise.',
            'Secure and functional contact form with reCAPTCHA for spam protection and automated email notifications to ensure reliable communication.',
            'User authentication system (login/logout/register) for future features, suchs as premium resources or client dashboards.',
            'Optimized for fast loading speeds and a smooth user experience across the site.'
        ],
        'screenshots': [
            'uase_website_screenshot_1.jpg',
        ],
        'downloads': [],
    },

    "it-consultancy": {
    "title": "IT Consultancy Website",
    "tagline": "Business consultancy and IT solutions for Nigerian companies.",
    "client_type": "Corporate Project",
    "category": "web-apps",
    "live_demo_link": "https://uase.tech",
    "github_link": None,
    "thumbnail": "projects/it_consultancy_thumbnail.jpg",
    "screenshots": [
        "projects/it_consultancy_1.png",
        "projects/it_consultancy_2.png",
        "projects/it_consultancy_3.png"
    ],
    "overview": "A Django-based corporate consultancy website tailored to Nigerian corporate needs. The platform provides IT and business services with a responsive, professional design, backend integration, and optimized CMS features.",
    "technologies": ["Django", "Bootstrap", "jQuery", "SQLite"],
    "expertise": "Backend integration, CMS design, corporate website development, and SEO optimization.",
    "features": [
        "Service listing and detailed descriptions",
        "Contact and inquiry forms with validation",
        "Responsive corporate theme for all devices",
        "SEO-optimized structure with clean URLs",
        "Easily extendable CMS for future services"
    ],
    "problem_solution": {
        "problem": "A Nigerian consultancy firm lacked an effective online presence to showcase their IT and business solutions.",
        "solution": "We developed a Django-powered corporate site with integrated service listings, responsive design, and SEO optimization, enabling the firm to reach more clients and improve credibility."
    },
    "downloads": []
},

'branding-identity-package': {
        'title': 'Brand Identity & Company Profile Design',
        'tagline': 'Crafting cohesive visual identities and professional company profiles for businesses.',
        'client_type': 'Various Businesses / Branding & Corporate Design',
        'category': 'ui-ux',
        'overview': 'Developed comprehensive brand identity packages for various businesses, including logo design, color palettes, typography, and visual guidelines. This service extends to **designing and restructuring professional company profiles and presentations**, ensuring a consistent and memorable brand presence across all digital and print media. Our work helps businesses establish a strong market identity and present themselves effectively to stakeholders, utilizing tools like CorelDRAW and Adobe Photoshop for high-quality visual outputs.',
        'technologies': ['Adobe Illustrator', 'Adobe Photoshop', 'CorelDRAW', 'Canva Pro', 'Color Theory', 'Typography Principles', 'Brand Guidelines Creation', 'Microsoft PowerPoint', 'Microsoft Word'],
        'expertise': [
            'Conducting in-depth brand research to understand client values and target audience.',
            'Designing unique and memorable logos that resonate with brand identity.',
            'Developing cohesive color palettes and typography systems for visual consistency.',
            'Creating comprehensive brand guidelines documents for consistent application.',
            'Producing versatile visual assets for various marketing channels (digital, print, merchandise).',
            '**Structuring and designing engaging company profiles, brochures, and presentations.**',
            '**Utilizing CorelDRAW and Adobe Photoshop for high-quality graphic design and image manipulation.**'
        ],
        'features': [
            'Primary and secondary logo designs.',
            'Defined brand color palette (CMYK, RGB, Hex codes).',
            'Recommended typography hierarchy.',
            'Usage guidelines for brand elements.',
            'Mockups demonstrating brand application on various collateral.',
            '**Professional company profile design and layout.**',
            '**Corporate presentation design and restructuring.**',
            '**Infographics and data visualization for reports.**'
        ],
        'screenshots': [],
        'live_demo_link': None,
        'github_link': None,
        'thumbnail': 'projects/branding_design.jpg',
        'problem_solution': {
            'problem': 'New businesses often lack a strong, cohesive visual identity and struggle to present their corporate profile professionally, leading to brand recognition issues and inconsistent messaging.',
            'solution': 'Created distinct brand identity packages and designed professional company profiles, brochures, and presentations. This provided businesses with unique logos, consistent visual elements, and clear guidelines, establishing a strong and memorable brand presence while enhancing their corporate communication using tools like CorelDRAW and Photoshop.'
        },
        'downloads': [],
    },

    'palatables-restaurant-concept': {
        'title': 'Palatables Restaurant Concept Site UI',
        'tagline': 'A modern UI/UX prototype for a hypothetical restaurant "Taste Haven by Jilong".',
        'client_type': 'Concept / UI/UX Design Study',
        'category': 'ui-ux',
        'live_demo_link': 'https://www.figma.com/proto/your-figma-link',
        'github_link': None,
        'thumbnail': 'projects/palatables_thumbnail.jpg',
        'screenshots': [
            'projects/palatables_screenshot_1.jpg',
            'projects/palatables_screenshot_2.jpg',
            'projects/palatables_screenshot_3.jpg',
        ],
        'overview': 'This project focuses purely on the UI/UX design aspect of a modern restaurant website. It features an elegant layout, intuitive navigation, and visually appealing elements designed to enhance the online dining experience for "Taste Haven by Jilong".',
        'technologies': ['Figma', 'Adobe XD', 'UI/UX Principles'],
        'features': [
            'Interactive menu display with high-quality images.',
            'Online reservation system concept.',
            'Responsive design for tablet and mobile viewing.',
            'Consistent branding and visual hierarchy.',
            'Smooth user flow for browsing and ordering.',
        ],
        'problem_solution': {
            'problem': 'Many restaurant websites are outdated or offer poor user experiences, hindering customer engagement and online ordering processes.',
            'solution': 'Designed a clean, modern, and highly intuitive UI/UX prototype for a hypothetical restaurant. The design prioritizes visual appeal, easy navigation, and seamless interaction, aiming to convert online visitors into actual diners.'
        },
        'downloads': []
    },

    '3-month-training-website': {
        'title': 'Empowering Futures: The 3-Month Training Platform',
        'tagline': 'An engaging landing page for a skill acquisition training program.',
        'client_type': 'Educational Institution / Skill Development Program',
        'category': 'training',
        'overview': "This project involved creating an engaging and informative landing page for a 3-month skill acquisition training program. The platform is designed to provide prospective students with all necessary details about the curriculum, schedule, and benefits, encouraging sign-ups. Its user-friendly interface and clear calls to action streamline the enrollment process, making essential information easily accessible.",
        'technologies': ['HTML5', 'CSS3', 'JavaScript', 'Bootstrap', 'MS Office Suite (for content preparation)'],
        'thumbnail': 'projects/3-month-training_thumbnail.jpg',
        'expertise': [
            'Designing responsive, mobile-first layouts using Bootstrap and custom CSS for broad accessibility and optimal viewing on any device.',
            'Creating user-experience focused UIs with clear calls to action (CTAs) and smooth scrolling navigation to guide users effectively.',
            'Implementing simple yet effective JavaScript interactivity for engaging animations and client-side form validation, enhancing user input quality.',
            'Structuring engaging and easily digestible content for effective knowledge transfer and high user retention in an educational context.'
        ],
        'features': [
            'Detailed training curriculum and schedule presentation.',
            'Engaging UI designed to drive registrations and inquiries through clear information display.',
            'Informational landing pages providing a comprehensive overview of the course.',
            'Prominent calls to action for easy enrollment.'
        ],
        'screenshots': [
            'training_website_screenshot_1.jpg',
            'training_website_screenshot_2.jpg',
        ],
        'live_demo_link': 'https://3days-website-training.vercel.app/',
        'github_link': 'https://github.com/UASE-TECH-STUDIO',
        'problem_solution': {
            'problem': 'Existing training programs lacked a structured, engaging, and accessible online platform for students to learn and track their progress effectively, particularly for a short, intensive course.',
            'solution': 'Developed a comprehensive e-learning landing page that offers structured course delivery and interactive content, designed to attract and inform prospective students about the 3-month skill acquisition program, facilitating effective enrollment and learning.'
        },
        'downloads': [],
    },
    '3-days-training-registration': {
        'title': 'Seamless Enrollment: 3-Days Training Registration Form',
        'tagline': 'A clean, intuitive, and responsive online registration form.',
        'client_type': 'Educational Program / Event Registration',
        'category': 'training',
        'overview': "This project focused on developing a clean, intuitive, and responsive online registration form for a short-term training program. Designed for efficient data capture, it incorporates robust client-side validation to ensure data accuracy and improve user experience. The form is built to be easily integrated with various backend systems or third-party form handling services, providing a seamless registration process for attendees.",
        'technologies': ['HTML', 'CSS', 'JavaScript', 'MS Office Suite (for data handling)', 'CorelDRAW (for form design elements)'],
        'thumbnail': 'projects/3-days-training_thumbnail.jpg',
        'expertise': [
            'Designing user-friendly and intuitive forms for efficient and accurate data collection.',
            'Implementing robust client-side input validation for improved data quality and enhanced user experience.',
            'Crafting clean and semantic HTML structure for superior accessibility and long-term maintainability.',
            'Applying responsive CSS for optimal display and usability across various devices, from desktops to mobile phones.',
            'Utilizing graphic design tools like CorelDRAW for visual elements and branding within forms.'
        ],
        'features': [
            'Efficient and secure collection of participant information.',
            'Real-time client-side validation to provide immediate feedback and guide users.',
            'Clean and minimalistic design for a straightforward and frictionless registration process.',
            'Integration-ready form for seamless backend processing or connection with third-party form handling services (e.g., Formspark).'
        ],
        'screenshots': [
            'training_registration_form_screenshot_1.jpg',
        ],
        'live_demo_link': 'https://3days-training-registration.vercel.app/',
        'github_link': 'https://github.com/UASE-TECH-STUDIO',
        'problem_solution': {
            'problem': 'The training program needed a dedicated, user-friendly, and reliable method for participants to register online, ensuring smooth data collection.',
            'solution': 'Developed a standalone, responsive registration form with robust client-side validation, ensuring efficient and secure collection of participant information, ready for backend integration.'
        },
        'downloads': [],
    },
  'student-age-calculator-web-app': {
        'title': 'Student Age Calculator Web App',
        'tagline': 'A simple, interactive web tool to calculate age from birthdate.',
        'client_type': 'Educational / Personal Project',
        'category': 'web-apps',
        'live_demo_link': 'https://your-live-demo-link.com/age-calculator',
        'github_link': 'https://github.com/UASE-TECH-STUDIO',
        'thumbnail': 'projects/age_calculator_thumbnail.jpg',
        'screenshots': [
            'projects/age_calculator_screenshot_1.jpg',
            'projects/age_calculator_screenshot_2.jpg',
        ],
        'overview': 'This project is a straightforward web application that allows users to input their birthdate and instantly see their current age. It showcases fundamental JavaScript DOM manipulation and basic web design principles, making it an excellent learning tool.',
        'technologies': ['HTML5', 'CSS3', 'JavaScript'],
        'features': [
            'User-friendly input for birthdate.',
            'Instant age calculation (years, months, days).',
            'Responsive design for various screen sizes.',
            'Clear error handling for invalid inputs.',
        ],
        'problem_solution': {
            'problem': 'The need for a simple, quick, and accessible tool for students or general users to calculate age without complex software installations.',
            'solution': 'Developed a lightweight, client-side web application using pure HTML, CSS, and JavaScript. The application runs directly in the browser, providing immediate results with a clean interface, ideal for quick calculations or educational demonstrations.'
        },
        'downloads': []
    },

    # --- New Projects Added Based on User Request ---
 'sales-record-analysis': {
        'title': 'Comprehensive Sales Record & Analysis',
        'tagline': 'Transforming raw sales data into actionable business insights.',
        'client_type': 'Various Businesses / Data Analysis',
        'category': 'others',
        'overview': 'Provided comprehensive services for collecting, organizing, and analyzing sales records from various companies. This project focuses on extracting key trends, identifying top-performing products/services, and generating insightful reports that empower businesses to make data-driven decisions and optimize sales strategies.',
        'technologies': ['Microsoft Excel (PivotTables, Charts)', 'Google Sheets', 'SPSS (basics)', 'Data Cleaning Techniques', 'Basic SQL (for data extraction)'],
        'expertise': [
            'Designing robust data collection and storage methodologies for sales records.',
            'Performing detailed data cleaning and validation to ensure accuracy.',
            'Utilizing advanced Excel functionalities for deep sales trend analysis and forecasting.',
            'Creating clear, impactful data visualizations and dashboards for executive reporting.',
            'Providing actionable insights and strategic recommendations based on sales performance data.',
        ],
        'features': [
            'Automated data aggregation from multiple sales channels.',
            'Interactive sales dashboards and performance indicators.',
            'Customer segmentation and buying pattern analysis.',
            'Revenue forecasting and trend identification.',
            'Customizable reports for different stakeholders.',
        ],
        'screenshots': [], # User will input later
        'live_demo_link': None,
        'github_link': None,
        'thumbnail': 'projects/sales_analysis.jpg', # Added placeholder thumbnail
        'problem_solution': {
            'problem': 'Businesses struggled to derive meaningful insights from their raw sales data, hindering strategic decision-making and growth.',
            'solution': 'Implemented a systematic approach to sales record analysis, utilizing advanced tools to clean, organize, and visualize data. This provided clear insights into sales performance, enabling businesses to optimize strategies and identify new opportunities.'
        },
        'downloads': [],
    },
    

    'edge-meter-stock-management': {
        'title': 'Edge Meter Stock Management System',
        'tagline': 'An efficient data entry and tracking solution for inventory.',
        'client_type': 'Client Project / Data Management',
        'category': 'others',
        'overview': 'Developed a tailored system for Edge Meter company to manage stock efficiently. This solution streamlines inventory tracking, ensuring accurate records and real-time insights into product availability and movement. It reduces manual errors and improves operational efficiency for inventory control.',
        'thumbnail': 'projects/stock_thumbnail.jpg',
        'technologies': ['Microsoft Excel (Advanced)', 'Google Sheets', 'Data Entry Principles', 'CSV/JSON handling (conceptual)'],
        'expertise': [
            'Designing and implementing robust data entry workflows for precise inventory management.',
            'Developing customized spreadsheets with advanced formulas and macros for automated stock tracking.',
            'Ensuring data integrity and consistency through rigorous validation processes.',
            'Creating intuitive interfaces for easy stock input, retrieval, and reporting.',
            'Providing comprehensive documentation and user training for seamless system adoption.',
        ],
        'features': [
            'Streamlined data entry forms for new stock and outgoing items.',
            'Automated inventory level tracking and alerts for low stock.',
            'Comprehensive reporting on stock movement, levels, and historical data.',
            'User-friendly interface for quick lookups and updates.',
            'Error detection and prevention mechanisms for data accuracy.',
        ],
        'screenshots': [], # User will input later
        'live_demo_link': None,
        'github_link': None,
        'problem_solution': {
            'problem': 'Edge Meter struggled with manual, error-prone stock management leading to inefficiencies and inventory discrepancies.',
            'solution': 'Implemented a custom data management system that automates stock tracking, reduces manual input errors, and provides real-time inventory insights, significantly improving operational efficiency and accuracy.'
        },
        'downloads': [],
    },
    'edge-meter-bid-preparation': {
        'title': 'Edge Meter Bid Preparation Applications',
        'tagline': 'Streamlining the process of creating winning bids and proposals.',
        'client_type': 'Client Project / Business Operations',
        'category': 'others',
        'overview': 'Developed tools and processes for Edge Meter to efficiently prepare detailed bids and proposals. This involves structuring critical project information, cost estimations, and service outlines into compelling and professional application documents, enhancing their success rate in securing new contracts.',
        'technologies': ['Microsoft Word (Advanced)', 'Microsoft Excel (Formulas & Templates)', 'PDF Generation Tools', 'Data Aggregation Techniques'],
        'expertise': [
            'Designing standardized templates for consistent and professional bid submissions.',
            'Developing automated tools within Excel for accurate cost estimation and proposal generation.',
            'Implementing version control strategies for collaborative bid preparation.',
            'Ensuring compliance with tender requirements and legal standards in document preparation.',
            'Training teams on efficient use of bid preparation tools and best practices.',
        ],
        'features': [
            'Customizable templates for various bid types and client requirements.',
            'Automated calculations for pricing and resource allocation.',
            'Version control and collaborative editing features.',
            'Integrated checklists for compliance and completeness.',
            'Export to professional PDF formats for submission.',
        ],
        'screenshots': [], # User will input later
        'live_demo_link': None,
        'github_link': None,
        'thumbnail': 'projects/bid_prep.jpg', # Added placeholder thumbnail
        'problem_solution': {
            'problem': 'Manual and inconsistent bid preparation processes led to delays and reduced competitiveness for Edge Meter.',
            'solution': 'Introduced a streamlined system with automated tools and standardized templates for bid preparation, significantly improving efficiency, accuracy, and the overall quality of proposals.'
        },
        'downloads': [],
    },
   
    
}

resources_data = {
    'html-css-beginner-pack': {
        'title': 'HTML & CSS Beginner Pack',
        'description': 'A complete starter guide for absolute beginners in web development. Includes sample projects, an HTML elements cheat sheet, and a CSS layout checklist.',
        'date_uploaded': 'April 18, 2025',
        'category': 'web-dev',
        'download_url': 'downloads/html_css_beginner_pack.zip',
        'download_name': 'Download Pack (ZIP)',
        'icon_class': 'bi-file-earmark-zip',
        'is_premium': False, # Not premium
    },
    'frontend-interview-checklist': {
        'title': 'Frontend Interview Preparation Checklist',
        'description': 'A curated checklist of HTML, CSS, JavaScript, and React questions. Perfect for those preparing for internships or junior developer roles.',
        'date_uploaded': 'March 22, 2025',
        'category': 'tech-skills',
        'download_url': 'downloads/frontend_interview_checklist.pdf',
        'download_name': 'Download PDF',
        'icon_class': 'bi-file-earmark-pdf',
        'is_premium': True, # Made premium
    },
    'academic-assignment-planner': {
        'title': 'Academic Assignment Planner',
        'description': 'An editable Google Sheets and Excel template for managing weekly assignments, deadlines, and revisions.',
        'date_uploaded': 'February 10, 2025',
        'category': 'academic',
        'download_url': 'downloads/academic_planner_template.zip',
        'download_name': 'Download Template (ZIP)',
        'icon_class': 'bi-file-earmark-spreadsheet',
        'is_premium': False, # Not premium
    },
    'freelancing-tech-guide': {
        'title': 'Guide: How to Start Freelancing in Tech (2025 Edition)',
        'description': 'Covers platforms, profile setup tips, gig optimization, and pricing strategies. Focused on virtual assistance, data entry, and design roles.',
        'date_uploaded': 'May 8, 2025',
        'category': 'business-tips',
        'download_url': 'downloads/freelancing_guide.pdf',
        'download_name': 'Download Guide (PDF)',
        'icon_class': 'bi-book',
        'is_premium': True, # Made premium
    },
    'javascript-snippets-beginners': {
        'title': 'JavaScript Snippets for Beginners',
        'description': 'Reusable mini-functions for common tasks like form validation, date formatting, age calculation, and DOM manipulation. Ready to use!',
        'date_uploaded': 'March 15, 2025',
        'category': 'web-dev',
        'download_url': 'downloads/javascript_snippets.zip',
        'download_name': 'Download Code Pack',
        'icon_class': 'bi-file-earmark-code',
        'is_premium': False, # Not premium
    },
    'python-data-analysis-cheatsheet': {
        'title': 'Python Data Analysis Cheatsheet',
        'description': 'A quick reference guide for essential Python libraries (Pandas, NumPy, Matplotlib) used in data analysis. Perfect for quick lookups.',
        'date_uploaded': 'January 5, 2025',
        'category': 'tech-skills',
        'download_url': 'downloads/python_data_analysis_cheatsheet.pdf',
        'download_name': 'Download PDF',
        'icon_class': 'bi-file-earmark-bar-graph',
        'is_premium': True, # Made premium
    },
    'basic-linux-commands': {
        'title': 'Basic Linux Commands Quick Reference',
        'description': 'A handy guide for essential Linux commands for developers, sysadmins, and students. Boost your command-line efficiency.',
        'date_uploaded': 'February 28, 2025',
        'category': 'tech-skills',
        'download_url': 'downloads/linux_commands_reference.pdf',
        'download_name': 'Download PDF',
        'icon_class': 'bi-terminal',
        'is_premium': False, # Not premium
    },
    'social-media-content-calendar': {
        'title': 'Social Media Content Calendar Template',
        'description': 'An editable template to plan and organize your social media content strategy. Essential for consistent online presence.',
        'date_uploaded': 'April 1, 2025',
        'category': 'business-tips',
        'download_url': 'downloads/social_media_calendar.xlsx',
        'download_name': 'Download Excel Template',
        'icon_class': 'bi-calendar-check',
        'is_premium': True, # Made premium
    },
    'project-management-checklist': {
        'title': 'Project Management Kickoff Checklist',
        'description': 'A comprehensive checklist to ensure a smooth and successful start to any new project. Covers planning, team setup, and initial communication.',
        'date_uploaded': 'May 15, 2025',
        'category': 'business-tips',
        'download_url': 'downloads/project_kickoff_checklist.pdf',
        'download_name': 'Download PDF',
        'icon_class': 'bi-check2-square',
        'is_premium': False, # Not premium
    },
    'web-accessibility-guide': { # New resource for general content
        'title': 'Web Accessibility Best Practices Guide',
        'description': 'A comprehensive guide to making your websites inclusive for all users, including those with disabilities. Covers WCAG guidelines and practical implementation tips.',
        'date_uploaded': 'June 1, 2025',
        'category': 'general-content', # New category
        'download_url': 'downloads/web_accessibility_guide.pdf',
        'download_name': 'Download Guide (PDF)',
        'icon_class': 'bi-universal-access', # Example icon for accessibility
        'is_premium': True, # Made premium
    },
}


# --- VIEW FUNCTIONS ---
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    return request.META.get('REMOTE_ADDR')


def home(request):
    testimonial_list = Testimonial.objects.order_by('-created_at')
    paginator = Paginator(testimonial_list, 5)
    page_number = request.GET.get('page')
    testimonials = paginator.get_page(page_number)
    return render(request, 'core/home.html', {'testimonials': testimonials})


def about(request):
    return render(request, 'core/about.html')


def services(request):
    # This view just renders the main services page.
    return render(request, 'core/services.html')



from django.shortcuts import render
from django.http import Http404

def service_detail(request, service_slug):
    services_data = {
        'web-development': {
            'title': 'Web Development & Engineering',
            'description': 'Building high-performance, type-safe web applications. We specialize in modern architectures that prioritize speed, security, and developer experience using industry-standard best practices like TDD.',
            'image_url': 'core/images/services/web_development.jpg',
            'tools_stack': ['TypeScript', 'RESTAPI', 'React.js', 'Next.js', 'FastAPI', 'Python (Django)', 'Tailwind CSS', 'PostgreSQL', 'TDD (PyTest/Jest)', 'RESTful APIs', 'Git/GitHub'],
            'benefits': ['Type-safe code for fewer bugs.', 'Scalable FastAPI backends.', 'TDD-backed reliability.', 'SEO-optimized Next.js structures.', 'Responsive modern UI.'],
            'how_we_work': ['Requirements & Logic Mapping.', 'API Design with FastAPI.', 'Frontend Implementation (TS/React).', 'Test-Driven Development (TDD) cycles.', 'Deployment & CI/CD.']
        },
        'software-development': {
            'title': 'Software Engineering',
            'description': 'Crafting robust software solutions using modern Python and TypeScript. We focus on clean code architecture and automated testing to solve complex business challenges.',
            'image_url': 'core/images/services/software_development.jpg',
            'tools_stack': ['Python', 'TypeScript', 'FastAPI', 'RESTAPI', 'Django', 'SQL/NoSQL', 'TDD', 'Docker', 'CLI Tools'],
            'benefits': ['Automated workflows.', 'Highly maintainable codebase.', 'Scalable system architecture.', 'Seamless API integrations.'],
            'how_we_work': ['System Architecture Planning.', 'Test-Driven Development (TDD).', 'Iterative Feature Sprints.', 'Rigorous QA & Bug Fixing.', 'Documentation & Deployment.']
        },
        'data-analysis-reports': {
            'title': 'Data Science & Analysis',
            'description': 'Transforming raw data into intelligence. We use powerful libraries to clean, analyze, and visualize complex datasets for research and business growth.',
            'image_url': 'core/images/services/data_analysis.jpg',
            'tools_stack': ['Python', 'RESTAPI', 'NumPy', 'Pandas', 'Matplotlib', 'SQL', 'SPSS', 'Advanced Excel'],
            'benefits': ['NumPy-powered computation.', 'Actionable business insights.', 'Statistically sound research.', 'Automated reporting pipelines.'],
            'how_we_work': ['Data Cleaning & Wrangling.', 'Exploratory Data Analysis (EDA).', 'Statistical Testing (NumPy/SPSS).', 'Interpretation & Visualization.', 'Final Reporting.']
        },
        'graphics-media-design': {
            'title': 'Graphics & Design',
            'description': 'Where code meets art. We don’t just draw; we engineer visuals. We specialize in generative design and high-fidelity branding using both traditional tools and code-driven graphic generation.',
            'image_url': 'core/images/services/graphics.jpg',
            'tools_stack': ['CorelDraw', 'Figma', 'Adobe Photoshop', 'Canva', 'Vs Code', 'Code-Driven Graphics',],
            'benefits': ['Unique Generative Designs.', 'Pixel-perfect UI Assets.', 'High-impact Brand Identity.', 'Mathematical precision in visuals.'],
            'how_we_work': ['Visual Logic Discovery.', 'Code-based sketching & prototyping.', 'High-fidelity design refinement.', 'Exporting for Web/Print.', 'Final Asset Delivery.']
        },
        'mobile-app-development': {
            'title': 'Web-to-Native Solutions',
            'description': 'Deploying powerful web applications to mobile environments. We use modern wrappers to ensure your business logic reaches users on their mobile devices efficiently.',
            'image_url': 'core/images/services/mobile_app.jpg',
            'tools_stack': ['Capacitor', 'TypeScript', 'Next.js', 'FastAPI (Backend)', 'Firebase'],
            'benefits': ['Cost-effective cross-platform.', 'Unified codebase.', 'Native device access.', 'Fast development cycles.'],
            'how_we_work': ['Web application optimization.', 'Mobile wrapper implementation.', 'Native feature integration.', 'Testing on physical devices.', 'APK/IPA generation.']
        },
        'data-entry-virtual-assistance': {
            'title': 'Virtual Assistance & Admin',
            'description': 'Technical administrative support. We use automation tools to handle your data entry and email marketing with surgical precision.',
            'image_url': 'core/images/services/va.jpg',
            'tools_stack': ['Google Workspace', 'Mailchimp', 'Excel Automation', 'Python Scripts', 'Slack'],
            'benefits': ['Reduced operational friction.', 'Automated repetitive tasks.', 'Accurate data management.', 'Professional communication.'],
            'how_we_work': ['Workflow audit.', 'Setup of automation scripts.', 'Task execution.', 'Quality assurance.', 'Weekly status reporting.']
        },
        'student-projects-academic-support': {
            'title': 'IT Project & Academic Support',
            'description': 'Guiding students through the complexities of Computer Science projects, focusing on modern stacks and proper documentation.',
            'image_url': 'core/images/services/academic.jpg',
            'tools_stack': ['Technical Writing', 'Algorithm Design', 'Python/TypeScript', 'TDD Basics', 'LaTeX'],
            'benefits': ['Deeper technical mastery.', 'Modern coding standards.', 'High-quality documentation.', 'Project defense readiness.'],
            'how_we_work': ['Topic assessment.', 'Technical guidance sessions.', 'Code review & debugging.', 'Research writing support.', 'Defense coaching.']
        },
        'tech-skills-training': {
            'title': 'Tech Skills & SIWES Mentorship',
            'description': 'Hands-on training for aspiring developers. We teach modern industry standards: from basic logic to TDD and building with FastAPI.',
            'image_url': 'core/images/services/training.jpg',
            'tools_stack': ['TypeScript', 'Python', 'FastAPI', 'Web Fundamentals', 'TDD'],
            'benefits': ['Industry-ready skills.', 'Project-based learning.', 'SIWES logbook support.', 'Modern tech mindset.'],
            'how_we_work': ['Skill gap analysis.', 'Curriculum delivery.', 'Live coding projects.', 'Progress evaluation.', 'Certification.']
        },
        'it-support-administration': {
            'title': 'Technical IT Administration',
            'description': 'Maintaining secure and efficient IT infrastructures. We provide troubleshooting, system optimization, and proactive tech support.',
            'image_url': 'core/images/services/it_support.jpg',
            'tools_stack': ['Windows/Linux Admin', 'Networking', 'Remote Support', 'System Security'],
            'benefits': ['Infrastructure stability.', 'Rapid problem resolution.', 'Data security.', 'Optimized productivity.'],
            'how_we_work': ['Audit & Health checks.', 'Optimization implementation.', 'Ongoing monitoring.', 'Vulnerability patching.', 'Reporting.']
        },
        'general-contracts-supplies': {
            'title': 'Contracts & Technical Supplies',
            'description': 'Under Usty Alhaji Service Enterprise, we procure high-end technical hardware and manage general service contracts with professional excellence.',
            'image_url': 'core/images/services/contract.jpg',
            'tools_stack': ['Hardware Procurement', 'Technical Vetting', 'Logistics', 'Supply Chain'],
            'benefits': ['Quality assurance.', 'Reliable sourcing.', 'Tech-spec compliance.', 'Official accountability.'],
            'how_we_work': ['Request for Quotation.', 'Procurement & Vetting.', 'Logistics Planning.', 'Delivery & Setup.']
        }
    }

def service_detail(request, service_slug):
    service = services_data.get(service_slug)
    if not service:
        raise Http404("Service not found.")
    return render(request, 'core/service_detail.html', {'service': service})

def portfolio(request):
    return render(request, 'core/portfolio.html', {'projects': projects_data})

def project_detail(request, project_slug):
    project = projects_data.get(project_slug) 
    if not project:
        raise Http404("Project not found")
    return render(request, 'core/project_detail.html', {
        'project': project,
        'MEDIA_URL': settings.MEDIA_URL,
    })

def resources(request):
    return render(request, 'core/resources.html', {'resources': resources_data})

def resume(request):
    return render(request, 'core/resume.html')

def graphics_portfolio(request):
    images = [f'graphic{i}.jpg' for i in range(1, 26)]
    return render(request, 'core/graphics_portfolio.html', {
        'images': images,
        'pdf_link': 'core/downloads/uase_graphics_catalog.pdf'
    })

# ===============================
# CONTACT & CRM
# ===============================

@csrf_exempt
def contact(request):
    if request.method != "POST":
        return render(request, "core/contact.html", {"form": ContactForm()})

    form = ContactForm(request.POST)
    recaptcha_token = request.POST.get("g-recaptcha-response")

    try:
        r = requests.post(
            "https://www.google.com/recaptcha/api/siteverify",
            data={
                "secret": settings.RECAPTCHA_SECRET_KEY,
                "response": recaptcha_token,
                "remoteip": request.META.get("REMOTE_ADDR"),
            }, timeout=5
        ).json()
    except Exception:
        return JsonResponse({"success": False, "message": "❌ reCAPTCHA verification failed."})

    if not r.get("success") or not form.is_valid():
        return JsonResponse({"success": False, "message": "❌ Invalid submission or reCAPTCHA failed.", "errors": form.errors})

    ip_address = get_client_ip(request)
    country = "Unknown"
    try:
        geo = requests.get(f"https://ipapi.co/{ip_address}/json/", timeout=4).json()
        country = geo.get("country_name", "Unknown")
    except: pass

    ContactMessage.objects.create(
        name=form.cleaned_data["name"],
        email=form.cleaned_data["email"],
        subject=form.cleaned_data.get("subject", "No Subject"),
        message=form.cleaned_data["message"],
        user=request.user if request.user.is_authenticated else None,
        ip_address=ip_address,
        country=country,
    )

    try:
        send_admin_notification({
            "name": form.cleaned_data["name"],
            "email": form.cleaned_data["email"],
            "subject": form.cleaned_data.get("subject"),
            "message": form.cleaned_data["message"],
            "ip_address": ip_address,
            "country": country,
        })
        send_user_confirmation(form.cleaned_data["name"], form.cleaned_data["email"])
    except:
        return JsonResponse({"success": False, "message": "❌ Message saved but email delivery failed."})

    return JsonResponse({"success": True, "message": "✅ Message sent successfully!"})

# ===============================
# ADMISSIONS / REGISTRATION
# ===============================

# ===============================
# ADMISSIONS / REGISTRATION
# ===============================

def register_view(request):
    # This context passes keys to your template
    context = {
        "flutterwave_public_key": getattr(settings, 'FLUTTERWAVE_PUBLIC_KEY', ''),
        "paystack_public_key": getattr(settings, 'PAYSTACK_PUBLIC_KEY', ''),
    }

    if request.method == 'POST':
        amount_map = {'launch': 20000, 'pro': 100000, 'fullstack': 150000, 'extra': 200000}
        program_slug = request.POST.get('program')
        payment_method = request.POST.get('payment_method')
        
        # Determine if payment is instant (Card) or needs verification (Transfer)
        # Note: 'paystack' and 'flutterwave' are card methods
        is_card = payment_method in ['paystack', 'flutterwave']

        # Capture reference from either Flutterwave or Paystack
        # The JS sends 'payment_ref' for Flutterwave and 'paystack_ref' for Paystack
        reference = request.POST.get('paystack_ref') or request.POST.get('payment_ref') or 'N/A'

        # Save the Registration and the File
        reg = ProgramRegistration.objects.create(
            name=request.POST.get('name'),
            email=request.POST.get('email'),
            phone=request.POST.get('phone'),
            whatsapp=request.POST.get('whatsapp'),
            program=program_slug,
            payment_method=payment_method,
            amount_paid=amount_map.get(program_slug, 0),
            transaction_ref=reference,
            payment_screenshot=request.FILES.get('payment_screenshot'),
            is_confirmed=True if is_card else False
        )

        # 1. Send Email Notification
        try:
            subject = "Registration Received - UASE Tech Studio"
            if is_card:
                message = f"Hi {reg.name}, your payment for the {reg.program} program has been confirmed! We will contact you on WhatsApp shortly to begin."
            else:
                message = f"Hi {reg.name}, we have received your payment proof for the {reg.program} program. Our team will verify the transfer and contact you shortly."
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [reg.email],
                fail_silently=True,
            )
        except:
            pass

        # 2. Return Response for AJAX/JavaScript
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success', 'message': 'Registration successful'})
            
        messages.success(request, "Registration submitted successfully!")
        return redirect('home')

    # This handles the GET request
    return render(request, 'core/registration.html', context)
# ===============================
# AUTHENTICATION & FILES
# ===============================

def register_user(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            login(request, form.save())
            messages.success(request, "Registration successful. Welcome!")
            return redirect('home')
        messages.error(request, "Registration failed.")
    return render(request, 'core/register.html', {'form': UserCreationForm()})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            messages.success(request, f"Welcome back, {form.cleaned_data.get('username')}!")
            return redirect('home')
        messages.error(request, "Invalid username or password.")
    return render(request, 'core/login.html', {'form': AuthenticationForm()})

@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('home')

@login_required
def upload_file(request):
    if request.method == 'POST' and request.FILES.get('file'):
        UploadedFile.objects.create(name=request.POST.get('name'), file=request.FILES['file'])
        messages.success(request, 'File uploaded successfully!')
        return redirect('upload_file')
    return render(request, 'core/upload.html')

# ===============================
# BLOG VIEWS
# ===============================

def blog_list(request):
    posts = Post.objects.all()
    page_obj = Paginator(posts, 6).get_page(request.GET.get('page'))
    return render(request, 'core/blog_list.html', {'page_obj': page_obj})

def blog_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)
    comments = post.comments.filter(is_approved=True)
    form = CommentForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        if request.user.is_authenticated:
            comment = form.save(commit=False)
            comment.post, comment.author = post, request.user
            comment.save()
            messages.success(request, "Your comment has been submitted!")
            return redirect('blog_detail', slug=post.slug)
        messages.error(request, "You must be logged in to comment.")
        return redirect('login')

    return render(request, 'core/blog_detail.html', {'post': post, 'comments': comments, 'comment_form': form})



# ===============================
# SYSTEM HANDLERS
# ===============================
def custom_404(request, exception): 
    return render(request, 'core/404.html', status=404)

def custom_500(request): 
    return render(request, 'core/500.html', status=500)