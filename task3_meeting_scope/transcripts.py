"""Three role-played meeting transcripts for evaluation.

Meeting 1: Initial scoping for a medical professionals directory
Meeting 2: Follow-up with scope changes (same client as Meeting 1)
Meeting 3: Initial scoping for a local restaurant directory (different client)
"""

MEETING_1_INITIAL = """
Client Sarah: Thanks for meeting with me today. I want to build an online directory for medical professionals in our region.

Consultant Alex: Great, happy to help. Can you tell me more about what you're envisioning?

Client Sarah: Sure. I want doctors, dentists, physiotherapists, and other healthcare providers to be able to create profiles with their qualifications, specialties, and clinic locations.

Consultant Alex: Got it. So a searchable directory of healthcare providers. What should visitors be able to do?

Client Sarah: Visitors should be able to search by specialty, location, and insurance accepted. They should also be able to read reviews from other patients.

Consultant Alex: Reviews are important. Do you want verified reviews only, or open reviews?

Client Sarah: Verified would be ideal. Maybe they have to confirm they actually visited the provider. But I understand that's harder to implement, so open reviews with moderation is fine as a starting point.

Consultant Alex: Makes sense. What about booking appointments?

Client Sarah: Yes! That's a must-have. Patients should be able to book appointments directly through the directory. Integration with common scheduling tools would be ideal.

Consultant Alex: What about the business model? How do you plan to monetize?

Client Sarah: I want a freemium model. Basic listings are free, but premium listings with featured placement, analytics, and the booking feature require a monthly subscription. I'm thinking three tiers: Free, Professional at $49/month, and Enterprise at $99/month.

Consultant Alex: Clear pricing structure. Any specific design preferences?

Client Sarah: Clean and trustworthy. Think WebMD meets Yelp. Mobile-first since most patients search on their phones. We need HIPAA compliance considerations too since we're dealing with healthcare.

Consultant Alex: Good point about HIPAA. What about the launch timeline?

Client Sarah: I'd like an MVP in 8 weeks. The full version with reviews and booking can follow in phase 2.

Consultant Alex: That's tight but doable for an MVP. Let me summarize what I'm hearing as must-haves for the MVP: provider profiles with qualifications, search by specialty and location, mobile-responsive design, and the freemium payment structure.

Client Sarah: Exactly. And I'd also like an admin dashboard where I can manage listings, approve new providers, and see basic analytics.

Consultant Alex: I'll include that. Anything else before I put together the scope?

Client Sarah: One more thing — I want to integrate with Google Maps for the location features. And eventually, I'd like a mobile app, but that can wait.

Consultant Alex: Noted. I'll prepare a detailed scope of work with hour estimates for you.
"""

MEETING_2_FOLLOWUP = """
Client Sarah: Hi Alex, thanks for the proposal. I've reviewed it with my business partner and we have some changes.

Consultant Alex: Of course. What would you like to adjust?

Client Sarah: First, we've decided to drop the review system entirely from the MVP. We'll add it in phase 2. It's too complex for our timeline.

Consultant Alex: That simplifies things. What else?

Client Sarah: We want to add a telemedicine feature. With everything going virtual, we need providers to offer video consultations directly through the platform.

Consultant Alex: That's a significant addition. Video calling requires WebRTC or integration with a service like Twilio. It will add substantial development time.

Client Sarah: I understand. But it's now a must-have for us. Our competitor just launched this and we can't be behind.

Consultant Alex: Got it, I'll add it. Anything else changed?

Client Sarah: The pricing tiers need to change. Instead of three tiers, we want just two: Free and Premium at $79/month. Simpler for users to understand.

Consultant Alex: So Free and Premium at $79, dropping the Enterprise tier. Noted.

Client Sarah: Also, we decided the mobile app is actually needed for the MVP now. At least a basic version for patients to search and book.

Consultant Alex: A mobile app for MVP is a big scope change. That could add 4-6 weeks depending on platform — iOS, Android, or both?

Client Sarah: Just iOS for now. We can do Android later.

Consultant Alex: OK. And the Google Maps integration is still in?

Client Sarah: Yes, that stays. But we want to increase the admin dashboard capabilities. We need real-time analytics, not just basic stats. Revenue tracking, user growth charts, that sort of thing.

Consultant Alex: So enhanced analytics dashboard. Let me note that the timeline will need to extend. With telemedicine and iOS app, we're looking at 12-14 weeks instead of 8.

Client Sarah: That's fine. We'd rather have it right than rush it.

Consultant Alex: I'll update the scope with these changes and send you a revised proposal with the new hour estimates and out-of-scope items.
"""

MEETING_3_RESTAURANT = """
Client Marco: Hello, I run a food blog and I want to turn it into a local restaurant directory for the Austin, Texas area.

Consultant Alex: Interesting. Tell me what you have in mind.

Client Marco: I want restaurant owners to claim their profiles and add menus, photos, hours, and special deals. Visitors should be able to search, filter by cuisine type, read reviews, and make reservations.

Consultant Alex: That's a full-featured directory. Let's break it down. What's most important for launch?

Client Marco: Search and filtering is number one. People need to find restaurants by cuisine, price range, neighborhood, and dietary options like vegan or gluten-free.

Consultant Alex: Makes sense. What about the restaurant profiles themselves?

Client Marco: Each restaurant should have a profile page with photos, menu, hours, location on a map, and contact info. I also want an integrated ordering system where users can place takeout orders.

Consultant Alex: Online ordering is complex. Are you thinking of building your own or integrating with existing services like DoorDash or Uber Eats?

Client Marco: Integration with existing services. I don't want to handle delivery logistics. Just let users click through to order from the restaurant's preferred delivery partner.

Consultant Alex: Smart approach. That's much simpler. What about monetization?

Client Marco: Restaurants pay to be featured. I want a sponsored listing option where restaurants pay $25/month to appear at the top of search results. Plus, I'll run local food brand advertisements.

Consultant Alex: So revenue from featured listings and ads. Got it. What about the review system?

Client Marco: Reviews are critical. I want a Yelp-style system with star ratings, written reviews, and photo uploads from diners. But I need strong moderation to prevent fake reviews. Maybe requiring a verified visit or minimum account age.

Consultant Alex: Anti-fraud measures for reviews add complexity but are important. What about your existing blog content?

Client Marco: I want to migrate my existing 200+ restaurant reviews from the blog into the directory. Each of my reviews should appear as an "Editor's Pick" or "Featured Review" on the restaurant's profile.

Consultant Alex: Blog migration with featured placement. Any technical requirements?

Client Marco: The site must be fast. Under 2-second load time. SEO is critical since we compete with Yelp and Google Maps locally. I also need a weekly email newsletter feature that highlights new restaurants and deals.

Consultant Alex: Performance and SEO noted. Timeline expectations?

Client Marco: I'd like to launch in 10 weeks. I have a food festival event in December where I want to debut the directory.

Consultant Alex: That's a firm deadline then. Let me prioritize: search, restaurant profiles with maps, featured listings, review system, and the blog migration. The newsletter and ad system could be phase 2 if time is tight.

Client Marco: The newsletter is important for my existing audience. Can we keep it in the MVP?

Consultant Alex: We can include a basic newsletter with curated content. Full automation with personalized recommendations would be phase 2.

Client Marco: Fair enough. Let's do that.

Consultant Alex: I'll draft the scope and proposal. One question — do you have budget constraints I should know about?

Client Marco: I can spend up to $15,000 on the initial build. After that, I need it to be self-sustaining through the featured listings revenue.

Consultant Alex: Good to know. I'll make sure the proposal fits within that budget. I'll have it to you by end of week.
"""

TRANSCRIPTS = [
    {
        "title": "Medical Directory - Initial Scoping",
        "meeting_type": "initial",
        "transcript": MEETING_1_INITIAL,
    },
    {
        "title": "Medical Directory - Follow-up Changes",
        "meeting_type": "follow_up",
        "transcript": MEETING_2_FOLLOWUP,
    },
    {
        "title": "Restaurant Directory - Initial Scoping",
        "meeting_type": "initial",
        "transcript": MEETING_3_RESTAURANT,
    },
]
