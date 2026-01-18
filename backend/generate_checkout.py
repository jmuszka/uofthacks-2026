
import json
import re
from urllib.parse import urlparse

# The raw input text from the user (pasted as-is)
input_text = r"""
"items":"[{\"title\":\"Letting Go High Cut Sneakers - Red\",\"price\":2099,\"description\":\"High cut red sneakers with a round toe and cushioned comfort for everyday wear.\",\"url\":\"https://www.fashionnova.com/products/letting-go-high-cut-sneakers-red?variant=39272969666684\",\"id\":\"gid://shopify/p/68ZTYQFw1ghKwWBi15PZyl\",\"image_url\":\"https://cdn.shopify.com/s/files/1/0293/9277/files/11-10-23Studio6_CB_LW_14-08-16_58_FERDI11_Red_15096_PXF.jpg?v=1725507331\"},{\"title\":\"Women's Osaka GP Challenge 1 Tennis Shoes Picante Red and Black\",\"price\":11390,\"description\":\"High-performance tennis shoes with Air Zoom support and enhanced stability for quick direction changes on hard courts.\",\"url\":\"https://tennisexpress.com/products/women-s-osaka-gp-challenge-1-tennis-shoes-picante-red-and-black?variant=50239798968635\",\"id\":\"gid://shopify/p/f7wHKmQopdVCeKVWuWe1Q\",\"image_url\":\"https://cdn.shopify.com/s/files/1/0887/5599/4939/files/HQ2553-600F25-2copy.webp?v=1764715812\"},{\"title\":\"Vision bright Canvas 100 Shoes Red\",\"price\":18500,\"description\":\"A bold, utilitarian low-top sneaker blending vintage-inspired design with modern luxury and street-ready durability.\",\"url\":\"https://valabasas.com/products/vision-bright-100-red?variant=45348598087865\",\"id\":\"gid://shopify/p/5tNhTkZP7Tny7MEs9RL5DJ\",\"image_url\":\"https://cdn.shopify.com/s/files/1/0506/1220/7801/files/vision-bright-100-shoes-red-6654912.jpg?v=1763744334\"},{\"title\":\"Kylie Flat Buckle Mary Janes-Post Box Red\",\"price\":10740,\"description\":\"A stylish Mary Jane and ballet pump hybrid designed for toddlers, offering comfort and versatility for early walkers.\",\"url\":\"https://us.boden.com/products/women-kylie-flat-buckle-mary-janes-post-box-red-a2038red?variant=47228566175996\",\"id\":\"gid://shopify/p/63o1a7ZWKqtiC0MWyERcRK\",\"image_url\":\"https://cdn.shopify.com/s/files/1/0680/4619/2892/files/25waut_a2038_red_247afbc8-21a7-47cc-8ee9-801cff103839.jpg?v=1753441514\"},{\"title\":\"Always A Classic Pump - Red\",\"price\":2399,\"description\":\"A stylish red slip-on dress pumps with ultra high heels and pointed toe for a chic, modern look.\",\"url\":\"https://www.fashionnova.com/products/always-a-classic-pump-red?variant=39252364198012\",\"id\":\"gid://shopify/p/3dPACnRrZGgBQ4wa3Xiqh7\",\"image_url\":\"https://cdn.shopify.com/s/files/1/0293/9277/products/10-22-21Studio6_SN_10-00-45_5_CONDITION39_Red_1826_KL.jpg?v=1725502894\"},{\"title\":\"Alpargata Red Heritage Canvas\",\"price\":5000,\"description\":\"Eco-friendly canvas slip-on shoes made with recycled materials and designed for comfort and sustainability.\",\"url\":\"https://checkout-us.toms.com/products/alpargata-women-red-heritage-canvas?variant=48359296205091\",\"id\":\"gid://shopify/p/3Sw3lixS3ddLOfpL5XMUk1\",\"image_url\":\"https://cdn.shopify.com/s/files/1/0741/0529/1043/files/10020789-s.jpg?v=1722004000\"},{\"title\":\"R.A.D® ONE V2 DEEP RED\",\"price\":15000,\"description\":\"A compact effects processor designed to enhance audio performance for fitness and gym environments.\",\"url\":\"https://rad-global.com/products/r-a-d-one-v2-marsala-black?variant=44875084628147\",\"id\":\"gid://shopify/p/6x1az0Xw6mK26L75J8ECrj\",\"image_url\":\"https://cdn.shopify.com/s/files/1/0579/5820/3571/files/01V2MARSALASIDE.jpg?v=1761128989\"},{\"title\":\"Limited Edition Romy Walking Shoes\",\"price\":4900,\"description\":\"Lightweight, orthotic-friendly walking shoes supporting heart health research with a limited edition design.\",\"url\":\"https://easyspirit.com/products/limited-edition-romy-walking-shoes-in-heart-red-e-romy40-mre01?variant=43103976292488\",\"id\":\"gid://shopify/p/3Oocbi1uU7Jnn5ZE5bmOkF\",\"image_url\":\"https://cdn.shopify.com/s/files/1/0274/3641/7160/files/3dd0d943009eb73825397ad133836558b4e31a6a.jpg?v=1732489477\"},{\"title\":\"Adidas Gazelle ADV Shoes - Shadow Red/Crystal White/Gold Metallic\",\"price\":9995,\"description\":\"Durable low-top sneakers with cushioned comfort and slip-resistant traction for versatile everyday wear.\",\"url\":\"https://shop.ccs.com/products/adidas-gazelle-adv-shoes-shadow-red-crystal-white-gold-metallic?variant=44516681056439\",\"id\":\"gid://shopify/p/hG9XW2k32vkFFKZfjdZvD\",\"image_url\":\"https://cdn.shopify.com/s/files/1/0519/1388/3831/files/197626461336-1.jpg?v=1757694992\"},{\"title\":\"Puma Suede XL 39520503 Mens Red Suede Lifestyle Sneakers Shoes\",\"price\":8500,\"description\":\"Classic red suede sneakers with a comfortable padded insole for extended wear and everyday style.\",\"url\":\"https://www.ruzeshoes.com/products/puma-suede-xl-39520503-mens-red-suede-lifestyle-sneakers-shoes-39520503_foralltimred_pm?variant=41457728880701\",\"id\":\"gid://shopify/p/5ammykztgIlgIQJcQMQb5C\",\"image_url\":\"https://cdn.shopify.com/s/files/1/0025/4823/6334/files/39520503-IMG6_01_a4d3902f-2428-401b-8b0a-cfa06625008b.jpg?v=1725858133\"}]"


{
    "items": "[{\"title\":\"Wally Braided - Blue Night\",\"price\":6499,\"description\":\"Lightweight and comfortable sneakers designed for everyday wear.\",\"url\":\"https://www.heydude.com/products/wally-braided-blue-night?variant=42682446118979\",\"id\":\"gid://shopify/p/72dKCwiz8HicXE1EHgx5Dg\",\"image_url\":\"https://cdn.shopify.com/s/files/1/0062/1532/files/40003-4NM.jpg?v=1765229919\"},{\"title\":\"Dunk Low Retro \\\"University Blue\\\"\",\"price\":14900,\"description\":\"A vintage-inspired Nike Dunk Low in University Blue, blending classic design with modern updates for sneaker enthusiasts.\",\"url\":\"https://gearwanta.com/products/dunk-low-retro-university-blue?variant=42085092294774\",\"id\":\"gid://shopify/p/2UyliRj71Vz2O5elHQdV9d\",\"image_url\":\"https://cdn.shopify.com/s/files/1/0020/5691/3014/files/Dunk-Low-Retro-University-Blue-1-GearWanta.png?v=1743696475\"},{\"title\":\"Wendy Stretch Sox - Blue Breeze\",\"price\":5499,\"description\":\"Lightweight, ventilated sneakers with drainage holes for all-day comfort and easy wear.\",\"url\":\"https://www.heydude.com/products/wendy-stretch-sox-bbr?variant=42098945851459\",\"id\":\"gid://shopify/p/4BXnsCxVxP0yqVpM5P2pfP\",\"image_url\":\"https://cdn.shopify.com/s/files/1/0062/1532/files/41878-4YQ_WENDYSTRETCHSOX_BLUEBREEZE_LEFT_SIDE_conversion1.jpg?v=1739381761\"},{\"title\":\"Wally Vintage Classic - Vintage Blue/Navy Blazer\",\"price\":5499,\"description\":\"A retro-inspired, lightweight blazer sneaker with vintage finish and modern comfort for everyday wear.\",\"url\":\"https://www.heydude.com/products/wally-vintage-classic-vintage-blue-navy-blazer?variant=42186832642115\",\"id\":\"gid://shopify/p/5dQGLj6nzHOiZVS0nMwUqD\",\"image_url\":\"https://cdn.shopify.com/s/files/1/0062/1532/files/44599-4YO_WALLYVINTAGECLASSIC_VINTAGEBLUENAVYBLAZER_LEFT_SIDE_conversion1.jpg?v=1751495429\"},{\"title\":\"Wally Hey2O Mesh - Sargasso Blue/Cloud Blue\",\"price\":6999,\"description\":\"Lightweight, ventilated sneakers with drainage holes for all-day comfort and easy wear.\",\"url\":\"https://www.heydude.com/products/wally-hey2o-mesh-sgb-cldb?variant=41315575726147\",\"id\":\"gid://shopify/p/18K7XnBVGKhSsOLDq70RV3\",\"image_url\":\"https://cdn.shopify.com/s/files/1/0062/1532/files/43145-4VW_WALLYHEY2OMESH_SARGASSOBLUE_CLOUDBLUE_LEFT_SIDE_1.jpg?v=1733265716\"},{\"title\":\"Men's Athens 2 - Naval Academy Blue\",\"price\":13995,\"description\":\"Hands-free athletic shoes designed for motion, comfort, and reliable traction.\",\"url\":\"https://kizik.com/products/mens-athens-2-naval-academy?variant=46266060669085\",\"id\":\"gid://shopify/p/7a2byJaHElbGxvPSVEoAqt\",\"image_url\":\"https://cdn.shopify.com/s/files/1/2281/1461/files/MATH2509_MENS_ATHENS_2_NAVAL_ACADEMY_Profile_Outer.png?v=1756916215\"},{\"title\":\"Men's OOmy Stride - Moroccan Blue\",\"price\":11995,\"description\":\"Cushioned, breathable athletic shoes designed for enhanced impact absorption and easy toe-off during activity or recovery.\",\"url\":\"https://www.oofos.com/products/mens-oomy-stride-moroccan-blue?variant=42980137500787\",\"id\":\"gid://shopify/p/36QfJnkhUa2Ya6iYExiXDn\",\"image_url\":\"https://cdn.shopify.com/s/files/1/0254/5969/files/5087MOROBLU_shot2.jpg?v=1744301623\"},{\"title\":\"Paul Washed - Vintage Blue/Multi\",\"price\":6499,\"description\":\"Lightweight, cushioned sneakers with a relaxed fit and easy on system for all-day comfort.\",\"url\":\"https://www.heydude.com/products/paul-washed-vbm?variant=42098966429763\",\"id\":\"gid://shopify/p/1vm2CH3vfm2HON4yzdJNHG\",\"image_url\":\"https://cdn.shopify.com/s/files/1/0062/1532/files/44290-4YN_PAULWASHED_VINTAGEBLUEMULTI_LEFT_SIDE_conversion1.jpg?v=1739396374\"},{\"title\":\"Tb.490 Club Suede Blue Leather Sneakers\",\"price\":20897,\"description\":\"Classic blue suede sneakers with a long tongue and exposed stitching, crafted for comfort and style.\",\"url\":\"https://alohas.com/products/tb-490-club-suede-blue-leather-sneakers?variant=48710811484496\",\"id\":\"gid://shopify/p/1dnOv5OIChsEstV5sCbPgA\",\"image_url\":\"https://cdn.shopify.com/s/files/1/0762/7039/files/E-COM-5-754_5690ab4d-f9ce-4168-8b63-7e996463474a.jpg?v=1757326018\"},{\"title\":\"Journey Mesh Blue (WWW)\",\"price\":21895,\"description\":\"Handcrafted men's athletic shoes with genuine leather and mesh uppers, offering all-day comfort, support, and moisture management for active lifestyles.\",\"url\":\"https://sasnola.com/products/journey-mesh-blue-www?variant=17542785564718\",\"id\":\"gid://shopify/p/5BY79ZE1fMDwNSsmSFlTEO\",\"image_url\":\"https://cdn.shopify.com/s/files/1/0018/7675/4478/products/journey-mesh-blue-www-mens-shoes-sas-shoes-369330.png?v=1725729733\"}]"
}
"""

all_items = []


# Try to find the JSON lists directly
# They start with "[{ and end with }]"
# But they are inside quotes in the input text, like "[{...}]"

matches = re.finditer(r'"(\[\{.*?\}\])"', input_text, re.DOTALL)

for match in matches:
    # content is the string INSIDE the quotes, e.g. [{...}]
    # It has escaped quotes like \"
    content = match.group(1)
    
    # Unescape: \" -> "
    # We also need to handle \\" just in case, but usually it's just \"
    clean_json = content.replace(r'\"', '"')
    
    try:
        data = json.loads(clean_json)
        all_items.extend(data)
    except Exception as e:
        print(f"Error parsing block: {e}")
        # Fallback: maybe it didn't need unescaping?
        try:
            data = json.loads(content)
            all_items.extend(data)
        except:
            pass

checkout_payload = []
for item in all_items:
    url = item.get('url', '')
    parsed = urlparse(url)
    domain = parsed.netloc
    
    # Extract variant ID from URL query param if possible
    query_params = {}
    if parsed.query:
        import urllib.parse
        query_params = urllib.parse.parse_qs(parsed.query)
    
    final_id = item.get('id')
    if 'variant' in query_params:
         final_id = query_params['variant'][0]
    
    if final_id and domain:
        checkout_payload.append({
            "variant_id": final_id,
            "quantity": 1,
            "store_domain": domain
        })

print(json.dumps({"items": checkout_payload}, indent=2))
