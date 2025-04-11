import os
import google.generativeai as genai
from google.api_core.exceptions import InvalidArgument
import logging
import re

# Set up logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

def clean_generated_content(content):
    """Remove common instruction messages from the generated content."""
    # List of patterns to remove (can be expanded as needed)
    patterns_to_remove = [
        r'```\s*Remember to replace.*?```',
        r'Remember to replace.*?correctly\.',
        r'<!-- Remember to replace.*?-->',
        r'/\* Remember to replace.*?\*/',
        r'Note: Replace.*?kit\.js',
        r'Remember to add your Font Awesome kit.*?\.',
        r'Replace the Font Awesome.*?icons\.',
        r'Remember to include.*?library\.',
        r'Make sure to add.*?CSS file\.',
        r'Don\'t forget to add.*?properly\.'
    ]
    
    # Apply each pattern
    for pattern in patterns_to_remove:
        content = re.sub(pattern, '', content, flags=re.DOTALL | re.IGNORECASE)
    
    return content

def generate_content(business_type, industry, business_name='', location='', description=''):
    """Generate website content using Google's Gemini AI model."""
    try:
        # Get API key from environment variables
        api_key = os.environ.get("GOOGLE_API_KEY")
        
        # Debug log the first few characters of the API key (never log full keys)
        if api_key:
            logger.info(f"API key found: {api_key[:4]}...")
        else:
            logger.error("API key not found in environment variables")
            raise ValueError("Google API key not found. Please check your .env file.")
        
        # Configure the Google AI API
        genai.configure(api_key=api_key)
        
        # Create a detailed prompt with styling information for modern websites
        prompt = f"""Generate a sophisticated, modern, fully-functioning HTML website for a {business_type} called "{business_name}" in the {industry} industry, located in {location}.

Business description: {description}

Requirements:
1. Create a complete HTML document with all necessary CSS included inline
2. Use a modern, sophisticated design that specifically matches the {industry} industry's aesthetics
3. Include high-quality color schemes and typography appropriate for {business_type}
4. Structure must include:
   - A striking hero section with compelling headline and sub-headline based on the business description
   - An "About Us" section with realistic, relevant content (NOT placeholder text)
   - Services/Products section with at least 3-4 specific offerings that would be realistic for this type of business
   - Testimonials section with 2-3 realistic testimonials (names and comments should reflect the business type)
   - Contact section with a working form layout and the business location
   - Footer with copyright, relevant links, and social icons

5. Use Bootstrap 5 for responsive layout and styling
6. Add subtle animations and transitions for modern feel
7. Ensure the written content is SPECIFIC to the business type, location and description - no generic placeholder text
8. Include Font Awesome icons (using CDN link) where appropriate
9. All text content should sound professional and be specific to this particular business
10. Every section should have coherent design that fits with the overall aesthetic
11. Include custom CSS that enhances the visual appeal beyond basic Bootstrap

DO NOT include any template instructions or placeholder comments in the final code.
"""
        try:
            # Generate content using Google's generative model
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)
            
            if response and hasattr(response, 'text'):
                # Clean the content before returning
                cleaned_content = clean_generated_content(response.text)
                
                # Apply a final cleanup to remove any remaining placeholder or lorem ipsum text
                cleaned_content = re.sub(r'Lorem ipsum.*?\.', '', cleaned_content, flags=re.DOTALL | re.IGNORECASE)
                
                return cleaned_content
            else:
                logger.error(f"Invalid response from Gemini API: {response}")
                raise ValueError("Received empty or invalid response from AI model")
                
        except Exception as model_error:
            logger.error(f"Error with Gemini model: {str(model_error)}")
            raise ValueError(f"Error generating content with Gemini: {str(model_error)}")
        
    except Exception as e:
        logger.error(f"Error in generate_content: {str(e)}")
        # If Google API fails, generate a basic modern template
        return f"""
        <div class="hero-section text-center py-5 bg-gradient-primary-to-secondary">
            <div class="container">
                <h1 class="display-4 fw-bold text-white">{business_name}</h1>
                <p class="lead mb-4 text-white-75">Premier {business_type} in {location} specializing in {industry} solutions</p>
                <button class="btn btn-light btn-lg rounded-pill px-4 shadow-sm">Learn More</button>
            </div>
        </div>
        
        <div class="about-section py-5">
            <div class="container">
                <div class="row align-items-center">
                    <div class="col-lg-6">
                        <h2 class="fw-bold mb-4">About Our Business</h2>
                        <p class="lead">{description}</p>
                        <p>At {business_name}, we combine years of experience in the {industry} industry with innovative approaches to deliver exceptional results. Our team of dedicated professionals is committed to exceeding client expectations.</p>
                    </div>
                    <div class="col-lg-6">
                        <div class="bg-light p-4 rounded-3 shadow-sm">
                            <h3 class="h5 fw-bold">Our Mission</h3>
                            <p>To provide outstanding {business_type} solutions that help our clients achieve their goals and grow their businesses in {location} and beyond.</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="services-section py-5 bg-light">
            <div class="container">
                <h2 class="text-center fw-bold mb-5">Our Services</h2>
                <div class="row g-4">
                    <div class="col-md-4">
                        <div class="card border-0 shadow-sm h-100 transition-hover">
                            <div class="card-body p-4">
                                <div class="icon-box mb-3 text-primary">
                                    <i class="bi bi-lightbulb fs-1"></i>
                                </div>
                                <h3 class="h5 card-title fw-bold">Premium {industry} Solutions</h3>
                                <p class="card-text">We deliver top-tier solutions tailored specifically to your business needs, helping you achieve optimal results in the competitive {industry} landscape.</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="card border-0 shadow-sm h-100 transition-hover">
                            <div class="card-body p-4">
                                <div class="icon-box mb-3 text-primary">
                                    <i class="bi bi-graph-up fs-1"></i>
                                </div>
                                <h3 class="h5 card-title fw-bold">Strategic Consulting</h3>
                                <p class="card-text">Our expert consultants provide in-depth analysis and strategic guidance based on years of experience in the {industry} sector.</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="card border-0 shadow-sm h-100 transition-hover">
                            <div class="card-body p-4">
                                <div class="icon-box mb-3 text-primary">
                                    <i class="bi bi-people fs-1"></i>
                                </div>
                                <h3 class="h5 card-title fw-bold">Dedicated Support</h3>
                                <p class="card-text">Our team provides responsive, professional support to ensure your ongoing success and satisfaction with our services.</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="testimonial-section py-5">
            <div class="container">
                <h2 class="text-center fw-bold mb-5">What Our Clients Say</h2>
                <div class="row g-4">
                    <div class="col-md-6">
                        <div class="card border-0 shadow-sm">
                            <div class="card-body p-4">
                                <p class="mb-3 text-warning">★★★★★</p>
                                <p class="card-text fst-italic">"{business_name} has transformed how we approach our business operations. Their expertise in {industry} has been invaluable to our growth and success."</p>
                                <div class="d-flex align-items-center mt-3">
                                    <div class="rounded-circle bg-primary text-white d-flex align-items-center justify-content-center" style="width: 50px; height: 50px;">JD</div>
                                    <div class="ms-3">
                                        <h6 class="mb-0">Michael Reynolds</h6>
                                        <small class="text-muted">Business Owner</small>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="card border-0 shadow-sm">
                            <div class="card-body p-4">
                                <p class="mb-3 text-warning">★★★★★</p>
                                <p class="card-text fst-italic">"Working with the team at {business_name} has been exceptional. Their understanding of {industry} challenges and innovative solutions set them apart from other providers."</p>
                                <div class="d-flex align-items-center mt-3">
                                    <div class="rounded-circle bg-primary text-white d-flex align-items-center justify-content-center" style="width: 50px; height: 50px;">LS</div>
                                    <div class="ms-3">
                                        <h6 class="mb-0">Laura Sanchez</h6>
                                        <small class="text-muted">Marketing Director</small>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="contact-section py-5 bg-light">
            <div class="container">
                <div class="row g-4">
                    <div class="col-lg-6">
                        <h2 class="fw-bold mb-4">Contact Us</h2>
                        <p class="mb-4">Get in touch with our team today to discuss how {business_name} can help you achieve your goals.</p>
                        <div class="d-flex mb-3">
                            <div class="me-3">
                                <i class="bi bi-geo-alt fs-4 text-primary"></i>
                            </div>
                            <div>
                                <h5 class="h6 mb-1">Address</h5>
                                <p class="mb-0">{location}</p>
                            </div>
                        </div>
                        <div class="d-flex mb-3">
                            <div class="me-3">
                                <i class="bi bi-envelope fs-4 text-primary"></i>
                            </div>
                            <div>
                                <h5 class="h6 mb-1">Email</h5>
                                <p class="mb-0">info@{business_name.lower().replace(' ', '')}.com</p>
                            </div>
                        </div>
                        <div class="d-flex">
                            <div class="me-3">
                                <i class="bi bi-telephone fs-4 text-primary"></i>
                            </div>
                            <div>
                                <h5 class="h6 mb-1">Phone</h5>
                                <p class="mb-0">(555) 123-4567</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-lg-6">
                        <div class="card border-0 shadow-sm">
                            <div class="card-body p-4">
                                <h3 class="h5 fw-bold mb-3">Send us a message</h3>
                                <form>
                                    <div class="mb-3">
                                        <input type="text" class="form-control" placeholder="Your Name">
                                    </div>
                                    <div class="mb-3">
                                        <input type="email" class="form-control" placeholder="Your Email">
                                    </div>
                                    <div class="mb-3">
                                        <textarea class="form-control" rows="4" placeholder="Your Message"></textarea>
                                    </div>
                                    <button type="submit" class="btn btn-primary w-100">Send Message</button>
                                </form>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <footer class="bg-dark text-white py-4 mt-5">
            <div class="container">
                <div class="row g-4">
                    <div class="col-lg-4">
                        <h3 class="h5 fw-bold mb-3">{business_name}</h3>
                        <p>Your trusted partner in the {industry} industry in {location}.</p>
                        <div class="social-links">
                            <a href="#" class="me-2 text-white"><i class="bi bi-facebook"></i></a>
                            <a href="#" class="me-2 text-white"><i class="bi bi-twitter"></i></a>
                            <a href="#" class="me-2 text-white"><i class="bi bi-instagram"></i></a>
                            <a href="#" class="me-2 text-white"><i class="bi bi-linkedin"></i></a>
                        </div>
                    </div>
                    <div class="col-lg-4">
                        <h3 class="h5 fw-bold mb-3">Quick Links</h3>
                        <ul class="list-unstyled">
                            <li class="mb-2"><a href="#" class="text-white text-decoration-none">Home</a></li>
                            <li class="mb-2"><a href="#" class="text-white text-decoration-none">About Us</a></li>
                            <li class="mb-2"><a href="#" class="text-white text-decoration-none">Services</a></li>
                            <li class="mb-2"><a href="#" class="text-white text-decoration-none">Contact</a></li>
                        </ul>
                    </div>
                    <div class="col-lg-4">
                        <h3 class="h5 fw-bold mb-3">Subscribe</h3>
                        <p>Stay updated with our latest news and offerings.</p>
                        <form class="d-flex">
                            <input type="email" class="form-control me-2" placeholder="Your Email">
                            <button type="submit" class="btn btn-primary">Subscribe</button>
                        </form>
                    </div>
                </div>
                <hr class="my-4">
                <p class="text-center mb-0">&copy; 2024 {business_name}. All rights reserved.</p>
            </div>
        </footer>
        
        <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css" rel="stylesheet">
        <style>
            .bg-gradient-primary-to-secondary {
                background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%);
            }
            .text-white-75 {
                color: rgba(255, 255, 255, 0.75);
            }
            .transition-hover {
                transition: transform 0.3s ease;
            }
            .transition-hover:hover {
                transform: translateY(-5px);
            }
        </style>
        """
