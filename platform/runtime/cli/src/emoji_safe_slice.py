"""
Emoji-safe string slicing utility for UNIBOS
Handles multi-byte unicode characters properly
"""

import unicodedata

try:
    import wcwidth
    WCWIDTH_AVAILABLE = True
except ImportError:
    WCWIDTH_AVAILABLE = False

def get_char_width(char):
    """Get display width of a character."""
    # Try wcwidth first if available
    if WCWIDTH_AVAILABLE:
        try:
            width = wcwidth.wcwidth(char)
            if width is not None:
                return width
        except:
            pass
    
    # Fallback: Check unicode category
    category = unicodedata.category(char)
    
    # Emoji ranges
    code = ord(char)
    
    # Common emoji ranges
    if 0x1F300 <= code <= 0x1F9FF:  # Emoticons, symbols, etc
        return 2
    elif 0x2600 <= code <= 0x27BF:  # Miscellaneous symbols
        return 2
    elif 0x1F000 <= code <= 0x1F02F:  # Mahjong/Domino
        return 2
    elif 0x1FA70 <= code <= 0x1FAFF:  # Extended symbols
        return 2
    elif code in [0x2764, 0x2763, 0x2665, 0x2666]:  # Hearts, etc
        return 2
    elif 0x1F680 <= code <= 0x1F6FF:  # Transport/Map symbols
        return 2
    elif 0x2700 <= code <= 0x27BF:  # Dingbats
        return 2
    
    # Zero-width characters
    if category in ('Mn', 'Me', 'Cf'):
        return 0
    
    # Default to 1 for normal characters
    return 1

def emoji_safe_slice(text, max_length):
    """
    Safely slice a string containing emojis and other unicode characters.
    Returns the sliced string padded to max_length.
    """
    if not text:
        return ' ' * max_length
    
    # Strip the text first to avoid leading/trailing spaces issues
    text = text.strip()
    
    # Count display width properly
    display_width = 0
    result = []
    
    i = 0
    while i < len(text) and display_width < max_length:
        char = text[i]
        
        # Handle emoji sequences (emoji + variation selector)
        if i + 1 < len(text) and ord(text[i + 1]) == 0xFE0F:
            # This is an emoji with variation selector
            char_width = 2
            if display_width + char_width <= max_length:
                result.append(text[i:i+2])
                display_width += char_width
            i += 2
        else:
            char_width = get_char_width(char)
            
            # Special handling for space
            if char == ' ':
                char_width = 1
            
            if display_width + char_width <= max_length:
                result.append(char)
                display_width += char_width
            else:
                break
            i += 1
    
    # Join the result
    final_text = ''.join(result)
    
    # Pad to fill the width
    padding_needed = max(0, max_length - display_width)
    
    return final_text + (' ' * padding_needed)

def get_display_width(text):
    """Calculate the actual display width of a string with emojis."""
    if not text:
        return 0
    
    width = 0
    i = 0
    while i < len(text):
        # Handle emoji sequences
        if i + 1 < len(text) and ord(text[i + 1]) == 0xFE0F:
            width += 2
            i += 2
        else:
            width += get_char_width(text[i])
            i += 1
    
    return width