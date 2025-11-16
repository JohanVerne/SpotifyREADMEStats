# Create an SVG infographic for the requested content type and time range
def create_spotify_infographic(
    stats_data: dict, section_type: str = "artists", time_range: str = "short_term"
) -> str:
    # Determine number of items and columns based on section type
    if section_type == "albums":
        num_columns = 3
        num_items = 3
        card_width = 280
        card_height = 350
    else:  # artists or songs
        num_columns = 5
        num_items = 5
        card_width = 180
        card_height = 280

    # Calculate SVG dimensions
    padding = 20
    card_spacing = 15
    title_height = 80
    total_width = (
        (card_width * num_columns) + (card_spacing * (num_columns - 1)) + (padding * 2)
    )
    total_height = card_height + title_height + padding

    # SVG header with styles
    svg_header = f"""<svg width="{total_width}" height="{total_height}" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
    <defs>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&amp;display=swap');
            .title {{ 
                fill: #1DB954; 
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; 
                font-size: 32px; 
                font-weight: 700; 
                letter-spacing: -0.5px;
            }}
            .subtitle {{
                fill: #B3B3B3;
                font-family: 'Inter', sans-serif;
                font-size: 14px;
                font-weight: 400;
            }}
            .card-title {{ 
                fill: #FFFFFF; 
                font-family: 'Inter', sans-serif; 
                font-size: 14px; 
                font-weight: 600; 
            }}
            .card-subtitle {{ 
                fill: #B3B3B3; 
                font-family: 'Inter', sans-serif; 
                font-size: 12px; 
                font-weight: 400; 
            }}
            .rank {{
                fill: #1DB954;
                font-family: 'Inter', sans-serif;
                font-size: 18px;
                font-weight: 700;
            }}
            .card {{
                transition: transform 0.2s;
            }}
        </style>
        <!-- Gradient for background -->
        <linearGradient id="bgGradient" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" style="stop-color:#191414;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#121212;stop-opacity:1" />
        </linearGradient>
        <!-- Card shadow filter -->
        <filter id="cardShadow" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur in="SourceAlpha" stdDeviation="3"/>
            <feOffset dx="0" dy="4" result="offsetblur"/>
            <feComponentTransfer>
                <feFuncA type="linear" slope="0.3"/>
            </feComponentTransfer>
            <feMerge>
                <feMergeNode/>
                <feMergeNode in="SourceGraphic"/>
            </feMerge>
        </filter>
        <!-- Clip path for rounded images -->
        <clipPath id="roundedImage">
            <rect width="100%" height="100%" rx="8" ry="8"/>
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
        title = "My Recently Saved Albums"
        subtitle = "Latest additions"
        data = stats_data.get("last_listened_to_albums", {})
    else:
        return None

    # Add title
    svg_content += f"""
    <text x="{padding}" y="45" class="title">{title}</text>
    <text x="{padding}" y="65" class="subtitle">{subtitle}</text>
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
        max_chars = 20 if section_type == "albums" else 15
        display_name = name if len(name) <= max_chars else name[: max_chars - 3] + "..."

        if section_type == "artists":
            subtitle_text = item.get("genre", "Unknown")
            subtitle_text = (
                subtitle_text
                if len(subtitle_text) <= max_chars
                else subtitle_text[: max_chars - 3] + "..."
            )
        else:
            artist_name = item.get("artist", "Unknown")
            subtitle_text = (
                artist_name
                if len(artist_name) <= max_chars
                else artist_name[: max_chars - 3] + "..."
            )

        # Image dimensions
        img_size = card_width - 20
        img_y_offset = 10

        # Card container with shadow
        svg_content += f"""
    <g class="card" filter="url(#cardShadow)">
        <!-- Card background -->
        <rect x="{x}" y="{y}" width="{card_width}" height="{card_height}" 
              fill="#282828" rx="12" ry="12"/>
        
        <!-- Rank badge -->
        <circle cx="{x + 20}" cy="{y + 20}" r="15" fill="#1DB954"/>
        <text x="{x + 20}" y="{y + 26}" class="rank" text-anchor="middle">{i+1}</text>
        """

        # Add image if available
        if image_url:
            svg_content += f"""
        <!-- Album/Artist Image -->
        <g clip-path="url(#roundedImage)">
            <image x="{x + 10}" y="{y + img_y_offset + 35}" width="{img_size}" height="{img_size}" 
                   href="{image_url}" preserveAspectRatio="xMidYMid slice"/>
        </g>
        """
        else:
            # Placeholder if no image
            svg_content += f"""
        <rect x="{x + 10}" y="{y + img_y_offset + 35}" width="{img_size}" height="{img_size}" 
              fill="#404040" rx="8" ry="8"/>
        <text x="{x + card_width/2}" y="{y + img_y_offset + 35 + img_size/2}" 
              class="card-subtitle" text-anchor="middle">No Image</text>
        """

        # Text section
        text_y = y + img_y_offset + img_size + 55

        svg_content += f"""
        <!-- Title -->
        <text x="{x + card_width/2}" y="{text_y}" class="card-title" text-anchor="middle">
            {display_name}
        </text>
        
        <!-- Subtitle -->
        <text x="{x + card_width/2}" y="{text_y + 20}" class="card-subtitle" text-anchor="middle">
            {subtitle_text}
        </text>
    </g>
    """

    # Footer with branding
    svg_content += f"""
    <text x="{total_width - padding}" y="{total_height - 10}" class="subtitle" text-anchor="end" opacity="0.5">
        Generated by SpotifyStats
    </text>
    """

    svg_footer = "</svg>"

    return svg_header + svg_content + svg_footer
