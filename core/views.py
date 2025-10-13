import json
import requests
from django.http import HttpResponse, JsonResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from .models import Testimonial, UploadedFile, ContactMessage, Post, Comment # Import new models
from .forms import ContactForm # You'll need to adjust this if you add a subject field to your form
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django import forms  # <--- Essential for using forms.Textarea
from django.forms import ModelForm # For CommentForm

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
    'web-development': {
        'title': 'Web Development',
        'description': 'Our web development service focuses on building responsive, visually appealing, and user-friendly websites. We help businesses, startups, and individuals establish a strong digital presence that reflects their brand identity and engages users effectively. Whether you\'re starting from scratch or need a site revamp, we tailor every project to meet your goals.',
        'image_url': 'core/images/services/web_development.jpg', # Example image path, ensure it exists
        'tools_stack': [
            'HTML5', 'CSS3', 'JavaScript', 'React.js', 'Next.js', 'Bootstrap', 'Tailwind CSS',
            'Python (Django, Flask)', 'Node.js (Express.js)', 'PHP',
            'MySQL', 'PostgreSQL', 'MongoDB', 'RESTful APIs', 'Git/GitHub', 'VS Code'
        ],
        'benefits': [
            'Fast, responsive websites that perform across all devices.',
            'SEO-friendly structure for better online visibility.',
            'Tailored design aligned with your brand identity and goals.',
            'Scalability – websites ready to grow with your business.',
            'Dedicated support after delivery for smooth operation.',
            'Affordable pricing suitable for students & startups.',
        ],
        'how_we_work': [
            '<strong>Consultation & Planning:</strong> We start with in-depth consultations to understand your goals, target audience, and specific functionalities needed.',
            '<strong>Design Phase:</strong> Creating wireframes, mockups, and prototypes to visualize the website structure and user flow.',
            '<strong>Development:</strong> Bringing the design to life with clean, efficient code for both front-end and optional backend functionalities.',
            '<strong>Testing & Feedback:</strong> Rigorous testing across various devices and browsers, followed by your feedback for final bug fixing and fine-tuning.',
            '<strong>Launch:</strong> Handling hosting setup, domain linking, and ensuring a smooth, secure launch of your website.',
            '<strong>Support:</strong> Providing optional maintenance plans and updates to keep your website performing optimally and securely.',
        ],
        'projects_linked': [
            {'name': 'UASE TECH-STUDIO Website (Your Current Site)', 'link': '/'},
            {'name': 'Student Age Calculator Web App', 'link': '/portfolio/student-age-calculator-web-app/'},
            {'name': 'Online Portfolio (React-based)', 'link': '/portfolio/online-portfolio-react/'},
            {'name': 'Palatables Restaurant Concept Site (UI prototype)', 'link': '/portfolio/palatables-restaurant-concept/'},
        ]
    },
    'software-development': {
        'title': 'Software Development',
        'description': 'We craft custom software applications that optimize your business processes, automate tasks, and solve unique challenges. From robust desktop solutions to complex enterprise systems, our software is built for high performance, security, and scalability, tailored to your exact operational needs.',
        'image_url': 'core/images/services/software_development.jpg',
        'tools_stack': [
            'Python', 'Django', 'Flask', 'Node.js', 'Express.js', 'Java', 'C++',
            'SQL (MySQL, PostgreSQL)', 'NoSQL (MongoDB)', 'Git/GitHub', 'VS Code', 'CLI',
            'MS Office Suite (for documentation/reporting)'
        ],
        'benefits': [
            'Automate manual tasks and reduce operational costs.',
            'Gain a competitive edge with proprietary tools.',
            'Enhance data security and integrity.',
            'Future-proof solutions designed for growth.',
            'Streamlined workflows and improved decision-making.',
        ],
        'how_we_work': [
            '<strong>Discovery & Planning:</strong> In-depth analysis of your requirements, scope definition, and technical architecture planning.',
            '<strong>Design & Prototyping:</strong> Designing system architecture and user interfaces for optimal usability and functionality.',
            '<strong>Agile Development:</strong> Iterative development sprints with continuous testing and client feedback integration.',
            '<strong>Quality Assurance:</strong> Comprehensive testing (unit, integration, UAT) to ensure a bug-free and secure application.',
            '<strong>Deployment & Training:</strong> Smooth deployment process followed by user training and comprehensive documentation.',
            '<strong>Maintenance & Support:</strong> Ongoing support, performance monitoring, and feature enhancements post-launch.',
        ],
        'projects_linked': [
            {'name': 'Internal Management System (Concept)', 'link': '#'},
            {'name': 'Custom CRM Tool (Prototype)', 'link': '#'},
        ]
    },
    'mobile-app-development': {
        'title': 'Mobile App Development',
        'description': 'Empower your business with intuitive and high-performing mobile applications for Android. Leveraging Flutter (for cross-platform) and Capacitor (for web-to-native conversions), we build apps that deliver seamless user experience, stunning design, and robust functionality, ensuring your brand reaches users on the go.',
        'image_url': 'core/images/services/mobile_app_development.jpg',
        'tools_stack': [
            'Flutter', 'Dart', 'Capacitor (for web-to-native conversion)', 'Firebase',
            'RESTful APIs', 'Provider/Bloc for State Management', 'Native Device Features (Camera, GPS)',
            'Git/GitHub', 'VS Code'
        ],
        'benefits': [
            'Wider audience reach across iOS and Android platforms.',
            'Enhanced user engagement with modern, fluid interfaces.',
            'Cost-effective development with cross-platform efficiency.',
            'Access to device hardware features for rich experiences.',
            'Direct communication channel with your customers.',
        ],
        'how_we_work': [
            '<strong>Idea Validation & Strategy:</strong> Refining your app concept, identifying key features, and strategizing user acquisition.',
            '<strong>UI/UX Design:</strong> Crafting wireframes, mockups, and interactive prototypes focused on mobile usability and aesthetics.',
            '<strong>Development Sprints:</strong> Building core functionalities in agile sprints, allowing for regular reviews and adjustments.',
            '<strong>Thorough Testing:</strong> Comprehensive testing on various devices and operating system versions to ensure stability and performance.',
            '<strong>App Store Submission:</strong> Guiding you through the process of submitting your app to Google Play Store and Apple App Store.',
            '<strong>Post-Launch Optimization:</strong> Providing ongoing updates, bug fixes, and performance monitoring for continued success.',
        ],
        'projects_linked': [
            {'name': 'Food Ordering Application (Web + Android APK)', 'link': '/portfolio/food-ordering-app/'},
        ]
    },
    'data-entry-virtual-assistance': {
        'title': 'Data Entry & Virtual Assistance',
        'description': 'Free up your valuable time by outsourcing routine administrative and data management tasks. We provide accurate, secure, and fast data handling, along with comprehensive remote administrative support, ensuring your operations run smoothly and efficiently without the overhead of additional staff.',
        'image_url': 'core/images/services/data_entry_virtual_assistance.jpg',
        'tools_stack': [
            'Microsoft Office Suite (Excel, Word, PowerPoint, Outlook)',
            'Google Workspace (Sheets, Docs, Gmail)',
            'Data Entry Software (various client-specific tools)',
            'CRM Software (basic navigation)',
            'Communication Platforms (Zoom, Slack, Google Meet)',
        ],
        'benefits': [
            'Significant time savings for core business activities.',
            'High accuracy and consistency in data management.',
            'Cost-effective solution, paying only for hours worked.',
            'Access to professional support without geographical limits.',
            'Improved operational efficiency and organization.',
        ],
        'how_we_work': [
            '<strong>Task Scoping:</strong> Understanding your specific data entry or virtual assistance needs and workflow.',
            '<strong>Secure Data Transfer:</strong> Establishing secure methods for data sharing and communication.',
            '<strong>Execution & Quality Check:</strong> Meticulous task completion with built-in quality assurance processes.',
            '<strong>Regular Updates:</strong> Providing consistent progress reports and status updates.',
            '<strong>Feedback Loop:</strong> Adapting to your preferences and incorporating feedback for continuous improvement.',
            '<strong>Confidentiality:</strong> Strict adherence to data privacy and confidentiality agreements.',
        ],
        'projects_linked': [
            {'name': 'Client Database Migration (Project X)', 'link': '#'},
            {'name': 'Ongoing Administrative Support for Company Y', 'link': '#'},
        ]
    },
    'student-projects-academic-support': {
        'title': 'Student Project & Academic Support',
        'description': 'Navigate complex computer science and IT academic challenges with expert guidance. We offer comprehensive support for SIWES reports, final year projects, research assistance, and academic writing, helping students achieve excellence and build confidence in their technical and research skills.',
        'image_url': 'core/images/services/student_projects_academic_support.jpg',
        'tools_stack': [
            'Problem Solving & Algorithm Design',
            'Programming Languages (Python, Java, C++, HTML, CSS, JavaScript)',
            'Database Management Systems (MySQL, PostgreSQL, MongoDB)',
            'Research Methodologies',
            'Documentation Tools (MS Word, LaTeX basics)',
            'Presentation Software (PowerPoint, Google Slides)',
        ],
        'benefits': [
            'Deeper understanding of academic concepts.',
            'High-quality, well-structured projects and reports.',
            'Enhanced problem-solving and coding abilities.',
            'Improved grades and academic standing.',
            'Confidence in tackling complex technical assignments.',
        ],
        'how_we_work': [
            '<strong>Project Brief Review:</strong> Thoroughly understanding your academic brief, guidelines, and specific areas requiring support.',
            '<strong>Concept Elucidation:</strong> Breaking down complex topics and clarifying methodologies relevant to your project.',
            '<strong>Guidance & Debugging:</strong> Providing expert advice on code structure, logic, and assisting with debugging efforts (we won\'t do it for you, but we\'ll guide you effectively).',
            '<strong>Research & Writing Support:</strong> Guiding you through research processes and refining academic writing for clarity and impact.',
            '<strong>Feedback & Revision:</strong> Offering constructive feedback on drafts and iterations to ensure academic rigor.',
            '<strong>Presentation Preparation:</strong> Assisting with clear and compelling presentation strategies for your project defense.',
        ],
        'projects_linked': [
            {'name': 'Guidance on a Final Year Project on AI', 'link': '#'},
            {'name': 'Debugging & Optimization for a Data Structures Assignment', 'link': '#'},
        ]
    },
    'tech-skills-training': {
        'title': 'Tech Skills Training',
        'description': 'Empower yourself or your team with in-demand digital skills. We offer practical, hands-on training and bootcamps in web development, UI/UX design, basic coding, and general ICT literacy. Our programs are designed to transform novices into proficient tech enthusiasts, ready for the digital age.',
        'image_url': 'core/images/services/tech_skills_training.jpg',
        'tools_stack': [
            'HTML, CSS, JavaScript',
            'Python Fundamentals',
            'UI/UX Design Tools (Figma, Adobe XD)',
            'Web Development Frameworks (Bootstrap, basics of React)',
            'General ICT Tools & Software',
            'Learning Management Systems (as platforms)',
        ],
        'benefits': [
            'Acquire practical, industry-relevant digital skills.',
            'Boost career prospects and marketability.',
            'Build a strong foundation for advanced tech studies.',
            'Gain confidence in navigating digital environments.',
            'Personalized learning paths and hands-on practice.',
        ],
        'how_we_work': [
            '<strong>Needs Assessment:</strong> Identifying your current skill level and learning objectives to tailor the training program.',
            '<strong>Custom Curriculum:</strong> Developing a curriculum that combines theoretical knowledge with practical, project-based exercises.',
            '<strong>Interactive Sessions:</strong> Delivering engaging sessions through live instruction, demonstrations, and Q&A.',
            '<strong>Hands-on Projects:</strong> Focusing on practical application through real-world mini-projects and coding challenges.',
            '<strong>Continuous Feedback:</strong> Providing regular feedback on progress and offering personalized guidance.',
            '<strong>Certification:</strong> Issuing certificates of completion for relevant bootcamps/courses.',
        ],
        'projects_linked': [
            {'name': 'Basic Web Development Bootcamp (Student Showcase)', 'link': '#'},
            {'name': 'Introduction to Python for Beginners Workshop', 'link': '#'},
        ]
    },
    'it-support-administration': {
        'title': 'IT Support & System Administration',
        'description': 'Ensure seamless operations and optimal performance with our comprehensive IT support and system administration services. We provide expert technical assistance, proactive system maintenance, and robust infrastructure management to keep your business running smoothly and securely.',
        'image_url': 'core/images/services/ict_problem_solving.jpg',
        'tools_stack': [
            'OS Installation/Configuration (Windows, Linux, macOS)',
            'Troubleshooting (Hardware, Software, Network)',
            'Remote Assistance Tools (e.g., TeamViewer, AnyDesk)',
            'Printer/Scanner Setup & Maintenance',
            'User Support & Training',
            'IT Asset & Documentation Management',
            'System Security Basics',
            'User Account Administration',
            'Backups & Recovery Solutions',
            'Helpdesk Tools',
            'MS Office Suite (Word, Excel, PowerPoint, Outlook)',
            'Networking (TCP/IP, DNS, DHCP, Router Configuration, LAN/WAN Diagnostics)',
            'Virtual Assisting Tools (e.g., Calendar Management, Email Management, Task Management Software)',
            'Graphic Editing Tools (e231.g., CorelDRAW, Basic Photoshop for IT-related graphics/documentation)',
        ],
        'benefits': [
            'Rapid resolution of technical issues, minimizing downtime.',
            'Optimized system performance and efficiency.',
            'Enhanced security against cyber threats.',
            'Expert advice for strategic IT decisions.',
            'Reduced frustration and improved productivity.',
        ],
        'how_we_work': [
            '<strong>Initial Diagnosis:</strong> Gathering information about the problem through detailed questioning and initial checks.',
            '<strong>Remote/On-site Troubleshooting:</strong> Utilizing appropriate tools and techniques to identify the root cause of the issue.',
            '<strong>Solution Implementation:</strong> Applying effective fixes, patches, or configuration changes.',
            '<strong>Verification & Testing:</strong> Ensuring the problem is fully resolved and systems are functioning as expected.',
            '<strong>Prevention & Recommendations:</strong> Advising on measures to prevent future issues and optimizing systems for long-term stability.',
            '<strong>Documentation:</strong> Providing clear explanations of the problem and its resolution for future reference.',
        ],
        'projects_linked': [
            {'name': 'Network Optimization for Small Office', 'link': '#'},
            {'name': 'Software Debugging & Patching for Client App', 'link': '#'},
        ]
    },
    'data-analysis-reports': {
        'title': 'Data Analysis & Reports',
        'description': 'Transform raw data into actionable insights. We offer data analysis services using tools like Excel, SPSS, and SQL for businesses, researchers, and students. From cleaning and organizing data to generating insightful reports and visualizations, we help you make data-driven decisions and present your findings clearly.',
        'image_url': 'core/images/services/data_analysis_reports.jpg',
        'tools_stack': [
            'Microsoft Excel (Advanced Functions, Pivot Tables)',
            'SPSS (Statistical Package for the Social Sciences)',
            'SQL (for database querying)',
            'Python (Pandas, NumPy for basic scripting)',
            'Data Visualization Tools (Tableau basics, Matplotlib basics)',
            'Google Sheets',
        ],
        'benefits': [
            'Clear, actionable insights from complex datasets.',
            'Improved decision-making based on factual data.',
            'Professional and visually appealing reports and presentations.',
            'Identification of trends, patterns, and opportunities.',
            'Time-saving for data cleaning and organization.',
        ],
        'how_we_work': [
            '<strong>Data Understanding:</strong> Discussing your data sources, objectives, and desired outcomes for the analysis.',
            '<strong>Data Cleaning & Preparation:</strong> Ensuring data quality, handling missing values, and formatting for analysis.',
            '<strong>Analysis Execution:</strong> Applying appropriate statistical or analytical methods using chosen tools.',
            '<strong>Report Generation:</strong> Creating comprehensive reports with clear explanations, charts, and visualizations.',
            '<strong>Insights & Recommendations:</strong> Translating findings into actionable recommendations for your business or research.',
            '<strong>Review & Revision:</strong> Collaborating to refine reports and ensure they meet your specific needs.',
        ],
        'projects_linked': [
            {'name': 'Market Research Data Analysis for Startup X', 'link': '#'},
            {'name': 'Sales Performance Report for Retail Business', 'link': '#'},
        ]
    },
    'graphics-media-design': {
        'title': 'Graphics & Media Design',
        'description': 'Create a powerful visual identity with our expert graphics and media design services. We craft engaging flyers, distinctive logos, compelling social media content, and full brand visuals that capture attention and effectively communicate your message, ensuring your brand stands out in a crowded digital landscape.',
        'image_url': 'core/images/services/graphics_media_design.jpg',
        'tools_stack': [
            'Adobe Photoshop',
            'Adobe Illustrator',
            'Canva Pro',
            'CorelDRAW',
            'Figma (for visual assets)',
        ],
        'benefits': [
            'Strong, memorable, and professional brand identity.',
            'Visually appealing marketing materials that attract clients.',
            'Consistent brand messaging across all platforms.',
            'Increased engagement and recall on social media.',
            'Clear communication through impactful infographics and visuals.',
        ],
        'how_we_work': [
            '<strong>Creative Briefing:</strong> Understanding your brand, target audience, design preferences, and project objectives.',
            '<strong>Concept Development:</strong> Brainstorming and sketching initial design concepts based on the brief.',
            '<strong>Design & Iteration:</strong> Digitally creating and refining designs, incorporating your feedback through revisions.',
            '<strong>Finalization & Delivery:</strong> Providing high-resolution files in various formats suitable for web, print, and other uses.',
            '<strong>Brand Guideline Support:</strong> Advising on how to maintain brand consistency for future design needs (optional).',
        ],
        'projects_linked': [
            {'name': 'Startup Logo & Brand Identity Package', 'link': '#'},
            {'name': 'Social Media Marketing Graphics for Event', 'link': '#'},
        ]
    },
    'lead-generation-online-growth': {
        'title': 'Lead Generation & Online Growth',
        'description': 'Supercharge your business growth by effectively identifying and nurturing potential clients. Our lead generation and online growth strategies focus on boosting your brand visibility, increasing website traffic, and converting prospects into loyal customers through targeted digital techniques.',
        'image_url': 'core/images/services/lead_generation_online_growth.jpg',
        'tools_stack': [
            'Digital Marketing Platforms (Google Ads, Facebook Ads basics)',
            'SEO Tools (Google Analytics, Keyword Planners basics)',
            'Social Media Management Tools',
            'Email Marketing Platforms',
            'Content Creation Tools',
            'CRM Integration (basic understanding)',
        ],
        'benefits': [
            'Increased qualified leads and potential customers.',
            'Improved brand awareness and online presence.',
            'Higher conversion rates and return on investment (ROI).',
            'Targeted marketing campaigns reaching the right audience.',
            'Measurable growth and actionable insights.',
        ],
        'how_we_work': [
            '<strong>Strategy Development:</strong> Defining your target audience, marketing goals, and crafting a tailored lead generation strategy.',
            '<strong>Content Creation:</strong> Developing engaging content (e.g., blog posts, social media updates, ad copy) to attract prospects.',
            '<strong>Campaign Implementation:</strong> Setting up and managing online advertising campaigns, SEO efforts, and social media promotions.',
            '<strong>Monitoring & Optimization:</strong> Continuously tracking performance metrics and optimizing campaigns for better results.',
            '<strong>Reporting & Analysis:</strong> Providing detailed reports on lead generation performance and growth metrics.',
            '<strong>Continuous Improvement:</strong> Adapting strategies based on market trends and performance data.',
        ],
        'projects_linked': [
            {'name': 'Social Media Growth Campaign for E-commerce', 'link': '#'},
            {'name': 'Website Traffic & SEO Improvement for Local Business', 'link': '#'},
        ]
    },
}

projects_data = {
     'food-ordering-app': {
        'title': 'Deliciously Simple: The Food Ordering Application (Web + Android APK)',
        'tagline': 'A full-stack food ordering platform with web and native Android APK access.',
        'client_type': 'Restaurant / Food Delivery Startup',
        'category': 'mobile-apps',
        'thumbnail': 'projects/food_thumbnail.jpg',
        'overview': (
            "The 'Deliciously Simple' Food Ordering Application is a comprehensive digital platform designed to revolutionize how customers order and manage their favorite meals. This full-stack solution, accessible via both a modern web interface and a native Android APK, empowers users to browse menus, customize orders, and make secure payments from the comfort of their homes. "
            "Customers can track their orders in real-time, view their complete order history, and even request modifications or cancellations (within defined parameters). "
            "For restaurant management, the application provides a powerful backend system to effortlessly edit and add menu items, control inventory, and manage user accounts. A standout feature is the integrated live chat system, allowing management to communicate directly with customers. This includes a pre-programmed bot for instant first replies, ensuring immediate customer engagement until a human representative takes over. "
            "Management can also efficiently oversee order fulfillment, adjust delivery times, and update order statuses, with all changes instantly reflected on the customer's order history page. "
            "Furthermore, the system includes robust user management capabilities, enabling administrators to edit user details upon request, block or delete users for policy violations, and control overall user access. "
            "A built-in newsletter subscription feature allows customers to opt-in for exclusive discounts and updates, fostering loyalty and driving repeat business. This application represents a seamless, intuitive, and feature-rich experience for both diners and food service providers."
        ),
        'technologies': ['React.js', 'Next.js', 'TypeScript', 'Tailwind CSS', 'Node.js', 'Express.js', 'MongoDB', 'Capacitor', 'Axios', 'Stripe API'],
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
            'food_ordering_app_screenshot_1.jpg',
            'food_ordering_app_screenshot_2.jpg',
            'food_ordering_app_screenshot_3.jpg',
            'food_ordering_app_screenshot_4.jpg',
            'food_ordering_app_screenshot_5.jpg',
            'food_ordering_app_screenshot_6.jpg',
            'food_ordering_app_screenshot_7.jpg',
            'food_ordering_app_screenshot_8.jpg',
        ],
        'live_demo_link': 'https://food-ordering-app-llk4.vercel.app/',
        'github_link': 'https://github.com/UASE-TECH-STUDIO',
        'problem_solution': {
            'problem': 'Many restaurants lacked a modern, efficient, and mobile-friendly way for customers to order food online, leading to missed sales and customer inconvenience, especially on mobile devices.',
            'solution': 'Developed a user-friendly web and native Android application that provides a smooth ordering experience, secure payments via Stripe, and real-time tracking. The use of React/Next.js and Capacitor ensured a high-performance, cross-platform solution, enhancing customer satisfaction and boosting restaurant sales.'
        },
        'downloads': [
            {'name': 'Download Android APK', 'file_url': 'food_ordering_app.apk'}
        ],
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


def service_detail(request, service_slug):
    service = services_data.get(service_slug)
    if not service:
        raise Http404("Service not found or coming soon!")
    
    context = {
        'service': service
    }
    return render(request, 'core/service_detail.html', context)


def portfolio(request):
    context = {
        'projects': projects_data
    }
    return render(request, 'core/portfolio.html', context)


def project_detail(request, project_slug):
    # This function now correctly references the global projects_data dictionary
    project = projects_data.get(project_slug) 
    if not project:
        raise Http404("Project not found")
    
    context = {
        'project': project,
        'MEDIA_URL': settings.MEDIA_URL,
    }
    return render(request, 'core/project_detail.html', context)

def resources(request):
    context = {
        'resources': resources_data # Pass the resources data to the template
    }
    return render(request, 'core/resources.html', context)


@login_required
def upload_file(request):
    if request.method == 'POST' and request.FILES.get('file'):
        UploadedFile.objects.create(
            name=request.POST.get('name'),
            file=request.FILES['file']
        )
        messages.success(request, 'File uploaded successfully!')
        return redirect('upload_file')
    return render(request, 'core/upload.html')


@csrf_exempt
def contact(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        form = ContactForm(request.POST)
        recaptcha_token = request.POST.get('g-recaptcha-response')

        recaptcha_secret = settings.RECAPTCHA_SECRET_KEY
        recaptcha_url = 'https://www.google.com/recaptcha/api/siteverify'
        recaptcha_data = {
            'secret': recaptcha_secret,
            'response': recaptcha_token,
            'remoteip': request.META.get('REMOTE_ADDR')
        }
        try:
            recaptcha_response = requests.post(recaptcha_url, data=recaptcha_data, timeout=5)
            recaptcha_response.raise_for_status()
            recaptcha_result = recaptcha_response.json()
        except requests.exceptions.RequestException as e:
            print(f"reCAPTCHA API request failed: {e}")
            return JsonResponse({'success': False, 'message': '❌ reCAPTCHA verification failed due to network error.'})
        except json.JSONDecodeError:
            print("reCAPTCHA API returned invalid JSON.")
            return JsonResponse({'success': False, 'message': '❌ reCAPTCHA verification failed due to invalid response.'})

        if not recaptcha_result.get('success'):
            print(f"reCAPTCHA verification failed: {recaptcha_result.get('error-codes')}")
            return JsonResponse({'success': False, 'message': '❌ reCAPTCHA failed. Please try again.'})

        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            message = form.cleaned_data.get('message', 'No Subject Provided') # Corrected to get 'message' as default
            subject = form.cleaned_data.get('subject', 'No Subject Provided')

            # Get the user if authenticated
            user_instance = request.user if request.user.is_authenticated else None
            
            ContactMessage.objects.create(name=name, email=email, subject=subject, message=message, user=user_instance)

            admin_full_message = f"Name: {name}\nEmail: {email}\nSubject: {subject}\n\nMessage:\n{message}"
            if user_instance:
                admin_full_message += f"\nSubmitted by (Logged-in User): {user_instance.username} (ID: {user_instance.id})"

            try:
                send_mail(
                    subject=f'New Contact Message from UASE Website: {subject}',
                    message=admin_full_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.CONTACT_RECIPIENT_EMAIL],
                    fail_silently=False,
                )
            except Exception as e:
                print(f"Error sending email to admin: {e}")
                return JsonResponse({'success': False, 'message': '❌ Message sent, but there was an error sending confirmation email to admin.'})

            try:
                send_mail(
                    subject='We received your message at UASE TECH-STUDIO',
                    message=f"Hi {name},\n\nThanks for reaching out! We’ve received your message and will reply soon.\n\nYour message:\n{message}",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    fail_silently=False,
                )
            except Exception as e:
                print(f"Error sending confirmation email to user: {e}")

            return JsonResponse({'success': True, 'message': '✅ Message sent successfully. We will reply shortly.'})
        else:
            return JsonResponse({'success': False, 'message': '❌ Please fill out all fields correctly.', 'errors': form.errors})
    else:
        form = ContactForm()
        return render(request, 'core/contact.html', {'form': form})


def resume(request):
    return render(request, 'core/resume.html')


# --- User Authentication Views ---
def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful. Welcome!")
            return redirect('home')
        else:
            messages.error(request, "Registration failed. Please correct the errors below.")
    else:
        form = UserCreationForm()
    return render(request, 'core/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {username}!")
                return redirect('home')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'core/login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('home')


# --- Blog Views ---
def blog_list(request):
    posts = Post.objects.all()
    paginator = Paginator(posts, 6) # Show 6 posts per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'core/blog_list.html', {'page_obj': page_obj})

def blog_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)
    comments = post.comments.filter(is_approved=True) # Only show approved comments
    new_comment = None
    
    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            if request.user.is_authenticated:
                new_comment = comment_form.save(commit=False)
                new_comment.post = post
                new_comment.author = request.user
                new_comment.save()
                messages.success(request, "Your comment has been submitted!")
                return redirect('blog_detail', slug=post.slug)
            else:
                messages.error(request, "You must be logged in to comment.")
                # You might want to redirect to login or show an inline message
                return redirect('login') # Or render the page again with an error on the form
    else:
        comment_form = CommentForm()

    return render(request, 'core/blog_detail.html', {
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
        'new_comment': new_comment # Pass this for potential feedback if comment was just added
    })


# --- Error Handlers (Optional but Recommended) ---
def custom_404(request, exception):
    return render(request, 'core/404.html', {}, status=404)

def custom_500(request):
    return render(request, 'core/500.html', {}, status=500)
