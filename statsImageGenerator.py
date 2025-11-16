import base64
import requests
import html


# Fetch an image from URL and convert to base64 data URI to bypass Github hotlinking restrictions
def fetch_image_as_base64(url):
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


# Wrap text to fit within max_width characters, returns list of lines
def wrap_text(text, max_width):
    words = text.split()
    lines = []
    current_line = []
    current_length = 0

    for word in words:
        if current_length + len(word) + len(current_line) <= max_width:
            current_line.append(word)
            current_length += len(word)
        else:
            if current_line:
                lines.append(" ".join(current_line))
            current_line = [word]
            current_length = len(word)

    if current_line:
        lines.append(" ".join(current_line))

    return lines[:2]  # Max 2 lines


# Escape XML special characters to prevent parsing errors
def escape_xml(text):
    if not text:
        return text
    return html.escape(text, quote=False)


# Create an SVG infographic for the requested content type and time range
def create_spotify_infographic(
    stats_data: dict, section_type: str = "artists", time_range: str = "short_term"
) -> str:

    # Determine number of items and columns based on section type
    if section_type == "last_albums":
        num_columns = 3
        num_items = 3
        card_width = 150
        card_height = 185  # Reduced height (no subtitle)
    else:  # artists or songs
        num_columns = 5
        num_items = 5
        card_width = 130
        card_height = 170  # Reduced height (no subtitle)

    # Calculate SVG dimensions - COMPACT
    padding = 12
    card_spacing = 8
    title_height = 55
    total_width = (
        (card_width * num_columns) + (card_spacing * (num_columns - 1)) + (padding * 2)
    )
    total_height = card_height + title_height + padding

    # SVG header with enhanced styles
    svg_header = f"""<svg width="{total_width}" height="{total_height}" xmlns="http://www.w3.org/2000/svg">
    <defs>
        <style type="text/css">
            .title {{ 
                fill: #1DB954; 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', Arial, sans-serif; 
                font-size: 22px; 
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
                line-height: 1.3;
            }}
        </style>
        <!-- Dark gradient background -->
        <linearGradient id="bgGradient" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" style="stop-color:#1a1a1a;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#0a0a0a;stop-opacity:1" />
        </linearGradient>
        <!-- Card gradient -->
        <linearGradient id="cardGradient" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" style="stop-color:#2a2a2a;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#1e1e1e;stop-opacity:1" />
        </linearGradient>
        <!-- Green accent gradient for hover effect -->
        <linearGradient id="accentGradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:#1DB954;stop-opacity:0.15" />
            <stop offset="100%" style="stop-color:#1ed760;stop-opacity:0.05" />
        </linearGradient>
        <!-- Subtle glow effect -->
        <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur in="SourceGraphic" stdDeviation="1" result="blur"/>
            <feComponentTransfer in="blur" result="glow">
                <feFuncA type="linear" slope="1.5"/>
            </feComponentTransfer>
            <feMerge>
                <feMergeNode in="glow"/>
                <feMergeNode in="SourceGraphic"/>
            </feMerge>
        </filter>
        <!-- Card shadow -->
        <filter id="cardShadow" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur in="SourceAlpha" stdDeviation="3"/>
            <feOffset dx="0" dy="2" result="offsetblur"/>
            <feComponentTransfer>
                <feFuncA type="linear" slope="0.3"/>
            </feComponentTransfer>
            <feMerge>
                <feMergeNode/>
                <feMergeNode in="SourceGraphic"/>
            </feMerge>
        </filter>
    </defs>
    
    <!-- Background with gradient -->
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

    # Add title with glow
    svg_content += f"""
    <g filter="url(#glow)">
        <text x="{padding}" y="32" class="title">{escape_xml(title)}</text>
    </g>
    <text x="{padding}" y="47" class="subtitle">{escape_xml(subtitle)}</text>
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

        # Wrap text instead of truncating
        max_chars = 18 if section_type == "last_albums" else 16
        name_lines = wrap_text(name, max_chars)

        # Image dimensions
        img_size = card_width - 16
        img_y_offset = 8

        # Card container with shadow and gradient
        svg_content += f"""
    <g class="card" filter="url(#cardShadow)">
        <!-- Card background with gradient -->
        <rect x="{x}" y="{y}" width="{card_width}" height="{card_height}" 
              fill="url(#cardGradient)" rx="10" ry="10"/>
        
        <!-- Subtle accent overlay -->
        <rect x="{x}" y="{y}" width="{card_width}" height="{card_height}" 
              fill="url(#accentGradient)" rx="10" ry="10" opacity="0.3"/>
        
        <!-- Top accent line -->
        <rect x="{x}" y="{y}" width="{card_width}" height="2" 
              fill="#1DB954" rx="10" ry="10" opacity="0.6"/>
        """

        # Fetch and embed image as base64 if available
        if image_url:
            base64_image = fetch_image_as_base64(image_url)
            if base64_image:
                svg_content += f"""
        <!-- Album/Artist Image (embedded as base64) -->
        <image x="{x + 8}" y="{y + img_y_offset}" width="{img_size}" height="{img_size}" 
               href="{base64_image}" preserveAspectRatio="xMidYMid slice"
               style="clip-path: inset(0% round 8px);"/>
        """
            else:
                # Placeholder if image fetch failed
                svg_content += f"""
        <rect x="{x + 8}" y="{y + img_y_offset}" width="{img_size}" height="{img_size}" 
              fill="#333333" rx="8" ry="8"/>
        <text x="{x + card_width/2}" y="{y + img_y_offset + img_size/2 + 5}" 
              class="card-title" text-anchor="middle" opacity="0.3" font-size="24">♪</text>
        """
        else:
            # Placeholder if no image URL
            svg_content += f"""
        <rect x="{x + 8}" y="{y + img_y_offset}" width="{img_size}" height="{img_size}" 
              fill="#333333" rx="8" ry="8"/>
        <text x="{x + card_width/2}" y="{y + img_y_offset + img_size/2 + 5}" 
              class="card-title" text-anchor="middle" opacity="0.3" font-size="24">♪</text>
        """

        # Text section with wrapped text (NO SUBTITLE)
        text_y = y + img_y_offset + img_size + 18

        # Title only (up to 2 lines, centered in remaining space)
        for line_idx, line in enumerate(name_lines):
            # Escape XML special characters
            escaped_line = escape_xml(line)
            svg_content += f"""
        <text x="{x + card_width/2}" y="{text_y + (line_idx * 13)}" class="card-title" text-anchor="middle">
            {escaped_line}
        </text>
        """

        svg_content += "</g>"

    svg_footer = "</svg>"

    return svg_header + svg_content + svg_footer
