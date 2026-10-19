"""50 test emails for evaluation.

Each email simulates a real customer scenario across the five categories:
question, bug_report, feature_request, billing, general.
"""

TEST_EMAILS = [
    # ── Questions (15) ───────────────────────────────────────────────────
    {
        "sender": "alice@example.com",
        "subject": "How do I create a new directory listing?",
        "body": "Hi, I just signed up for Brilliant Directories and I'm trying to create my first listing. Can you walk me through the steps? I don't see any 'Add Listing' button on my dashboard.",
    },
    {
        "sender": "bob@startup.io",
        "subject": "Customizing the member profile page",
        "body": "How can I customize what fields appear on member profiles? I want to add a custom 'Specialization' dropdown field. Is this possible without coding?",
    },
    {
        "sender": "carol@design.co",
        "subject": "SEO settings for my directory",
        "body": "Where do I configure the SEO settings? I want to set meta titles and descriptions for each category page. Also, does the platform generate a sitemap automatically?",
    },
    {
        "sender": "dave@agency.com",
        "subject": "How to set up membership payment plans",
        "body": "I want to offer monthly and annual payment plans for premium listings. How do I configure the payment gateway and create different subscription tiers?",
    },
    {
        "sender": "emma@local.biz",
        "subject": "Embedding directory on my existing website",
        "body": "Can I embed my Brilliant Directories site into my existing WordPress website? If so, how? I'd like it to appear as a subdirectory, not a subdomain.",
    },
    {
        "sender": "frank@corp.net",
        "subject": "How to add a blog section",
        "body": "Does Brilliant Directories support a blog? I'd like to publish articles related to my industry directory. How do I set it up?",
    },
    {
        "sender": "grace@school.edu",
        "subject": "Importing existing member data",
        "body": "I have a CSV file with 500 members from our old system. How can I bulk import them into Brilliant Directories? What format does the CSV need to be in?",
    },
    {
        "sender": "henry@shop.com",
        "subject": "Setting up email notifications",
        "body": "How do I configure email notifications? I want members to receive a welcome email when they sign up and a reminder when their listing is about to expire.",
    },
    {
        "sender": "irene@media.org",
        "subject": "Adding a deals or coupons section",
        "body": "I want my directory members to be able to post special deals or coupons. Is there a built-in feature for this, or do I need a plugin?",
    },
    {
        "sender": "jack@dev.io",
        "subject": "API access for directory data",
        "body": "Does Brilliant Directories have an API? I need to pull listing data into our mobile app. What endpoints are available and how do I authenticate?",
    },
    {
        "sender": "karen@health.org",
        "subject": "How to moderate new listings",
        "body": "I want to review and approve new listings before they go live. Is there a moderation queue? How do I set it up so nothing publishes without my approval?",
    },
    {
        "sender": "leo@travel.com",
        "subject": "Multi-language support",
        "body": "Can I run my directory in multiple languages? I need English and Spanish versions. Is there a built-in translation feature?",
    },
    {
        "sender": "mia@food.co",
        "subject": "Adding map view to listings",
        "body": "How do I enable the map view for directory listings? I want visitors to see all restaurants plotted on a Google Map. Do I need a Google Maps API key?",
    },
    {
        "sender": "noah@legal.firm",
        "subject": "Setting up lead generation forms",
        "body": "I want visitors to be able to send inquiries directly to listed lawyers through a contact form on each profile. How do I enable this? Can I track how many leads each listing receives?",
    },
    {
        "sender": "olivia@events.com",
        "subject": "How to add an events calendar",
        "body": "My directory members want to post upcoming events. Is there a calendar feature? Can visitors filter events by date, location, or category?",
    },
    # ── Bug Reports (10) ─────────────────────────────────────────────────
    {
        "sender": "pete@web.dev",
        "subject": "Search not returning results",
        "body": "The search function on my directory has stopped working. When I type anything and hit search, it shows 'No results found' even for listings I know exist. This started yesterday after I updated a plugin.",
    },
    {
        "sender": "quinn@store.com",
        "subject": "Payment form broken on checkout",
        "body": "Customers are reporting that the payment form doesn't load on the checkout page. They see a blank white space where the form should be. This is happening on Chrome and Firefox. Urgent - we're losing sales!",
    },
    {
        "sender": "rachel@design.co",
        "subject": "Images not uploading to listings",
        "body": "I can't upload images to any listing. I get an error message saying 'Upload failed: file too large' even though my images are only 200KB. This was working fine last week.",
    },
    {
        "sender": "sam@tech.io",
        "subject": "Mobile layout completely broken",
        "body": "The mobile version of my directory is showing everything in a single column with text overlapping. The navigation menu doesn't open. This started after the latest update.",
    },
    {
        "sender": "tina@art.gallery",
        "subject": "Email notifications not sending",
        "body": "None of my automated emails are being sent. New member welcome emails, inquiry notifications, nothing is going out. I've checked spam folders and the SMTP settings look correct.",
    },
    {
        "sender": "uma@fitness.co",
        "subject": "Login page showing 500 error",
        "body": "When members try to log in, they get a 500 Internal Server Error page. This affects all users. I haven't changed any settings. Can you please look into this immediately?",
    },
    {
        "sender": "victor@auto.com",
        "subject": "Duplicate listings appearing",
        "body": "After the last import, I'm seeing duplicate listings for about 30 members. When I try to delete the duplicates, it also removes the original. Please help!",
    },
    {
        "sender": "wendy@beauty.salon",
        "subject": "Categories not displaying correctly",
        "body": "My category pages are broken. Some categories show listings from other categories, and two of my categories just show blank pages. The category tree seems jumbled.",
    },
    {
        "sender": "xander@finance.co",
        "subject": "SSL certificate not working on custom domain",
        "body": "I connected my custom domain last week and the SSL doesn't seem to be active. Browsers show 'Not Secure' warning. I followed the DNS setup instructions exactly.",
    },
    {
        "sender": "yara@music.fm",
        "subject": "Dashboard analytics showing wrong numbers",
        "body": "The analytics dashboard shows 0 visitors for the past week, but I know we've had traffic because I can see it in Google Analytics. Something is broken with the built-in stats.",
    },
    # ── Feature Requests (10) ────────────────────────────────────────────
    {
        "sender": "adam@startup.co",
        "subject": "Suggestion: Add review system for listings",
        "body": "It would be great to have a review and rating system where visitors can leave star ratings and written reviews on listings. Many of our members have asked for this. Could you add it?",
    },
    {
        "sender": "beth@marketing.io",
        "subject": "Feature request: Social media integration",
        "body": "I'd love a feature where new listings automatically post to our directory's Facebook and Twitter accounts. Also, could members connect their social profiles to their listings?",
    },
    {
        "sender": "chris@realestate.com",
        "subject": "Request: Advanced search filters",
        "body": "We need more advanced search filters — price range sliders, multi-select dropdowns for amenities, and the ability to save search criteria. The current search is too basic for our real estate directory.",
    },
    {
        "sender": "diana@edu.org",
        "subject": "Wish: Comparison feature for listings",
        "body": "Could you add a feature where visitors can select 2-3 listings and compare them side by side? This would be really helpful for our educational institution directory.",
    },
    {
        "sender": "ethan@food.app",
        "subject": "Enhancement: Mobile app for directory members",
        "body": "Would it be possible to create a companion mobile app? Members could manage their listings, respond to inquiries, and check their analytics from their phones.",
    },
    {
        "sender": "fiona@wellness.co",
        "subject": "Feature: Booking integration",
        "body": "I'd love to integrate appointment booking directly into member profiles. Could you add Calendly or a native booking feature so visitors can schedule appointments with listed professionals?",
    },
    {
        "sender": "george@photo.studio",
        "subject": "Request: Portfolio/gallery feature for listings",
        "body": "Photographers in our directory need to showcase their work. Could you add a portfolio or gallery section to listings that supports image galleries with lightbox viewing?",
    },
    {
        "sender": "hannah@nonprofit.org",
        "subject": "Suggestion: Volunteer matching feature",
        "body": "For our nonprofit directory, it would be amazing to have a volunteer matching feature where organizations can post volunteer opportunities and individuals can apply directly through the platform.",
    },
    {
        "sender": "ian@sports.club",
        "subject": "Feature: Team/group listings",
        "body": "We need the ability to create group or team listings where multiple members are grouped under one organization. Currently, each person needs their own separate listing which is confusing.",
    },
    {
        "sender": "julia@fashion.co",
        "subject": "Enhancement: Video support in listings",
        "body": "Members want to add video content to their listings — product demos, introductions, etc. Could you add native video upload or at least YouTube/Vimeo embed support?",
    },
    # ── Billing (10) ─────────────────────────────────────────────────────
    {
        "sender": "kyle@biz.com",
        "subject": "Need invoice for last month",
        "body": "Hi, can you send me the invoice for my September payment? I need it for our accounting. My account email is kyle@biz.com and I'm on the Professional plan.",
    },
    {
        "sender": "laura@agency.net",
        "subject": "Want to upgrade my plan",
        "body": "I'm currently on the Basic plan but I need more features. Can I upgrade to Professional mid-cycle? Will I be charged the full price or prorated?",
    },
    {
        "sender": "mike@store.co",
        "subject": "Unexpected charge on my card",
        "body": "I was charged $299 yesterday but my plan is $99/month. Can you explain this charge? I didn't authorize any upgrades or add-ons.",
    },
    {
        "sender": "nancy@consulting.biz",
        "subject": "Cancel my subscription",
        "body": "I need to cancel my Brilliant Directories subscription effective immediately. Please confirm that no further charges will be made and let me know about data retention.",
    },
    {
        "sender": "oscar@media.co",
        "subject": "Refund request",
        "body": "I signed up 3 days ago and the platform doesn't meet our needs. I'd like to request a full refund. I haven't added any content yet. Do you have a money-back guarantee?",
    },
    {
        "sender": "paula@dental.care",
        "subject": "Payment method update",
        "body": "My credit card on file is expiring next month. How do I update my payment method? I don't want any interruption in service.",
    },
    {
        "sender": "quentin@law.firm",
        "subject": "Annual vs monthly pricing",
        "body": "I've been paying monthly at $99/month. I see there's an annual plan. How much do I save? Can I switch to annual billing and what happens to my current billing cycle?",
    },
    {
        "sender": "rosa@hotel.com",
        "subject": "Billing discrepancy in member payments",
        "body": "Several of our directory members are reporting that they were charged twice for their listing subscription this month. Can you check the billing system? Here are the affected accounts: member IDs 4521, 4522, 4530.",
    },
    {
        "sender": "steve@gym.fit",
        "subject": "Custom pricing for my directory members",
        "body": "I want to offer different pricing tiers for my directory members — free, silver, gold, and platinum. Can I customize the member subscription pricing and what features each tier gets?",
    },
    {
        "sender": "tracy@wedding.co",
        "subject": "Tax invoice requirements",
        "body": "We need invoices that include our EU VAT number for tax purposes. Is it possible to add a VAT ID field to the billing system? Our VAT number is EU1234567.",
    },
    # ── General (5) ──────────────────────────────────────────────────────
    {
        "sender": "ursula@pr.agency",
        "subject": "Partnership opportunity",
        "body": "Hi team, we run a PR agency that works with several industry associations. We'd love to discuss a potential partnership where we refer clients to Brilliant Directories. Who should I speak with?",
    },
    {
        "sender": "vince@blog.com",
        "subject": "Can I write a review of your platform?",
        "body": "I'm a tech blogger and I'd like to write a detailed review of Brilliant Directories for my audience. Could you provide me with a trial account and any press materials?",
    },
    {
        "sender": "wanda@school.edu",
        "subject": "Student project using your platform",
        "body": "I'm a computer science student and I'd like to use Brilliant Directories for my capstone project. Do you offer educational discounts or free accounts for students?",
    },
    {
        "sender": "xavier@ngo.org",
        "subject": "Nonprofit discount availability",
        "body": "We're a registered 501(c)(3) nonprofit. Do you offer any discounts or special pricing for nonprofit organizations? We'd be using the directory to connect volunteers with opportunities.",
    },
    {
        "sender": "zoe@creative.co",
        "subject": "Feedback on your new interface",
        "body": "Just wanted to say the new dashboard design looks great! Much easier to navigate. One small thing — the color contrast on the sidebar links could be a bit stronger for accessibility. Otherwise, love the update!",
    },
]

# Validate we have exactly 50
assert len(TEST_EMAILS) == 50, f"Expected 50 test emails, got {len(TEST_EMAILS)}"
