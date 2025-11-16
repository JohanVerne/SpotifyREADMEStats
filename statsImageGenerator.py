import base64
import requests


def fetch_image_as_base64(url):
    """
    Fetch an image from URL and convert to base64 data URI
    """
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        img_base64 = base64.b64encode(response.content).decode("utf-8")

        # Determine image type from URL or content-type
        content_type = response.headers.get("content-type", "image/jpeg")
        return f"data:{content_type};base64,{img_base64}"
    except Exception as e:
        print(f"Error fetching image from {url}: {e}")
        return None


# Create an SVG infographic for the requested content type and time range
def create_spotify_infographic(
    stats_data: dict, section_type: str = "artists", time_range: str = "short_term"
) -> str:

    # Determine number of items and columns based on section type
    if section_type == "last_albums":
        num_columns = 3
        num_items = 3
        card_width = 140
        card_height = 200
    else:  # artists or songs
        num_columns = 5
        num_items = 5
        card_width = 120
        card_height = 180

    # Calculate SVG dimensions
    padding = 15
    card_spacing = 10
    title_height = 60
    total_width = (
        (card_width * num_columns) + (card_spacing * (num_columns - 1)) + (padding * 2)
    )
    total_height = card_height + title_height + padding

    # SVG header with INLINE styles (no external fonts)
    svg_header = f"""<svg width="{total_width}" height="{total_height}" xmlns="http://www.w3.org/2000/svg">
    <defs>
        <style type="text/css">
            .title {{ 
                fill: #1DB954; 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', Arial, sans-serif; 
                font-size: 24px; 
                font-weight: 700; 
            }}
            .subtitle {{
                fill: #B3B3B3;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
                font-size: 11px;
                font-weight: 400;
            }}
            .card-title {{ 
                fill: #FFFFFF; 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; 
                font-size: 11px; 
                font-weight: 600; 
            }}
            .card-subtitle {{ 
                fill: #B3B3B3; 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; 
                font-size: 9px; 
                font-weight: 400; 
            }}
        </style>
        <!-- Gradient for background -->
        <linearGradient id="bgGradient" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" style="stop-color:#191414;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#121212;stop-opacity:1" />
        </linearGradient>
        <!-- Card shadow filter -->
        <filter id="cardShadow" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur in="SourceAlpha" stdDeviation="2"/>
            <feOffset dx="0" dy="2" result="offsetblur"/>
            <feComponentTransfer>
                <feFuncA type="linear" slope="0.2"/>
            </feComponentTransfer>
            <feMerge>
                <feMergeNode/>
                <feMergeNode in="SourceGraphic"/>
            </feMerge>
        </filter>
        <!-- Clip path for rounded images -->
        <clipPath id="roundedImage">
            <rect width="100%" height="100%" rx="6" ry="6"/>
        </clipPath>
    </defs>
    
    <!-- Background -->
    <rect width="{total_width}" height="{total_height}" fill="url(#bgGradient)"/>
    """

    # Title section
    svg_content = ""

    if section_type == "artists":
        if time_range == "short_term":
            title = "My Recent Top Artists"
            subtitle = "Last 4 weeks"
            data = stats_data.get("top_artists", {}).get("short_term", {})
        else:
            title = "My All-Time Top Artists"
            subtitle = "All time favorites"
            data = stats_data.get("top_artists", {}).get("long_term", {})

    elif section_type == "top_songs":
        if time_range == "short_term":
            title = "My Recent Top Songs"
            subtitle = "Last 4 weeks"
            data = stats_data.get("top_songs", {}).get("short_term", {})
        else:
            title = "My All-Time Top Songs"
            subtitle = "All time favorites"
            data = stats_data.get("top_songs", {}).get("long_term", {})

    elif section_type == "last_albums":
        title = "Recently Saved Albums"
        subtitle = "Latest additions"
        data = stats_data.get("last_listened_to_albums", {})
    else:
        return None

    # Add title
    svg_content += f"""
    <text x="{padding}" y="35" class="title">{title}</text>
    <text x="{padding}" y="50" class="subtitle">{subtitle}</text>
    """

    # Create cards
    y_start = title_height

    for i, (idx, item) in enumerate(list(data.items())[:num_items]):
        # Calculate position
        col = i % num_columns
        x = padding + (col * (card_width + card_spacing))
        y = y_start

        # Get item data
        name = item.get("name", "Unknown")
        image_url = item.get("image", None)

        # Truncate long names
        max_chars = 14 if section_type == "last_albums" else 12
        display_name = name if len(name) <= max_chars else name[: max_chars - 2] + ".."

        if section_type == "artists":
            subtitle_text = item.get("genre", "Unknown")
            subtitle_text = (
                subtitle_text
                if len(subtitle_text) <= max_chars
                else subtitle_text[: max_chars - 2] + ".."
            )
        else:
            artist_name = item.get("artist", "Unknown")
            subtitle_text = (
                artist_name
                if len(artist_name) <= max_chars
                else artist_name[: max_chars - 2] + ".."
            )

        # Image dimensions
        img_size = card_width - 16
        img_y_offset = 8

        # Card container with shadow
        svg_content += f"""
    <g class="card" filter="url(#cardShadow)">
        <!-- Card background -->
        <rect x="{x}" y="{y}" width="{card_width}" height="{card_height}" 
              fill="#282828" rx="8" ry="8"/>
        """

        # Fetch and embed image as base64 if available
        if image_url:
            base64_image = fetch_image_as_base64(image_url)
            if base64_image:
                svg_content += f"""
        <!-- Album/Artist Image (embedded as base64) -->
        <image x="{x + 8}" y="{y + img_y_offset}" width="{img_size}" height="{img_size}" 
               href="{base64_image}" preserveAspectRatio="xMidYMid slice"
               style="clip-path: inset(0% round 6px);"/>
        """
            else:
                # Placeholder if image fetch failed
                svg_content += f"""
        <rect x="{x + 8}" y="{y + img_y_offset}" width="{img_size}" height="{img_size}" 
              fill="#404040" rx="6" ry="6"/>
        """
        else:
            # Placeholder if no image URL
            svg_content += f"""
        <rect x="{x + 8}" y="{y + img_y_offset}" width="{img_size}" height="{img_size}" 
              fill="#404040" rx="6" ry="6"/>
        """

        # Text section
        text_y = y + img_y_offset + img_size + 18

        svg_content += f"""
        <!-- Title -->
        <text x="{x + card_width/2}" y="{text_y}" class="card-title" text-anchor="middle">
            {display_name}
        </text>
        
        <!-- Subtitle -->
        <text x="{x + card_width/2}" y="{text_y + 14}" class="card-subtitle" text-anchor="middle">
            {subtitle_text}
        </text>
    </g>
    """

    svg_footer = "</svg>"

    return svg_header + svg_content + svg_footer
