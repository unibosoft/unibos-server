#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
unibos ASCII Art Logo Designs
Showcasing different styles for the splash screen
"""

class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    ORANGE = "\033[38;5;208m"
    WHITE = "\033[37m"
    YELLOW = "\033[33m"
    CYAN = "\033[36m"

def print_design(name, logo_lines, color=Colors.ORANGE):
    """Print a logo design with header"""
    print(f"\n{'='*80}")
    print(f"{Colors.BOLD}{name}{Colors.RESET}")
    print(f"{'='*80}\n")
    
    for line in logo_lines:
        # Replace COLOR placeholder with actual color
        formatted_line = line.replace("COLOR", color).replace("RESET", Colors.RESET)
        print(formatted_line)
    print()

# Design 1: Block Style (Modern, Bold)
design1 = [
    "",
    "COLOR██   ██ ███    ██ ██ ██████   ██████  ███████RESET",
    "COLOR██   ██ ████   ██ ██ ██   ██ ██    ██ ██     RESET",
    "COLOR██   ██ ██ ██  ██ ██ ██████  ██    ██ ███████RESET", 
    "COLOR██   ██ ██  ██ ██ ██ ██   ██ ██    ██      ██RESET",
    "COLOR ██████  ██   ████ ██ ██████   ██████  ███████RESET",
    ""
]

# Design 2: Double-line Box Drawing (Professional)
design2 = [
    "",
    "COLOR╔╗ ╔╗╔═╗╔╗╔╦╗╔═╗╔═╗╔═╗RESET",
    "COLOR║║ ║║║ ║║║║║║║ ║║ ║║ ╗RESET",
    "COLOR║║ ║║║ ║║║║║║║╔╝║ ║╚═╗RESET",
    "COLOR║║ ║║║ ║║║║║║║╚╗║ ║╔═╝RESET",
    "COLOR║╚═╝║║ ║║║║║║║╚╝║ ║╚═╗RESET",
    "COLOR╚═══╝╚═╝╚╝╚╩╝╚══╚═╝╚═╝RESET",
    ""
]

# Design 3: 3D Shadow Effect (Eye-catching)
design3 = [
    "",
    "COLOR██╗   ██╗███╗   ██╗██╗██████╗  ██████╗ ███████╗RESET",
    "COLOR██║   ██║████╗  ██║██║██╔══██╗██╔═══██╗██╔════╝RESET",
    "COLOR██║   ██║██╔██╗ ██║██║██████╔╝██║   ██║███████╗RESET",
    "COLOR██║   ██║██║╚██╗██║██║██╔══██╗██║   ██║╚════██║RESET",
    "COLOR╚██████╔╝██║ ╚████║██║██████╔╝╚██████╔╝███████║RESET",
    "COLOR ╚═════╝ ╚═╝  ╚═══╝╚═╝╚═════╝  ╚═════╝ ╚══════╝RESET",
    ""
]

# Design 4: Simple ASCII (Cross-platform compatible)
design4 = [
    "",
    "COLOR                                                RESET",
    "COLOR ##   ## ###   ## ## #####   #####  ##### RESET",
    "COLOR ##   ## ####  ## ## ##  ## ##   ## ##    RESET",
    "COLOR ##   ## ## ## ## ## #####  ##   ## ##### RESET",
    "COLOR ##   ## ##  #### ## ##  ## ##   ## ##    RESET",
    "COLOR  #####  ##   ### ## #####   #####  ##### RESET",
    "COLOR                                                RESET",
    ""
]

# Design 5: Minimalist Style (Clean)
design5 = [
    "",
    "COLOR┬ ┬┌┐┌┬┌┐ ┌─┐┌─┐RESET",
    "COLOR│ │││││├┴┐│ │└─┐RESET",
    "COLOR└─┘┘└┘┴└─┘└─┘└─┘RESET",
    ""
]

# Design 6: Banner Style with Shading
design6 = [
    "",
    "COLOR▄   ▄ ▄▄  ▄ ▄ ▄▄▄   ▄▄▄  ▄▄▄RESET",
    "COLOR█   █ █ █ █ █ █  █ █   █ █   RESET",
    "COLOR█   █ █  ██ █ ███  █   █ ███ RESET",
    "COLOR█   █ █   █ █ █  █ █   █   █ RESET",
    "COLOR ███  █   █ █ ███   ███  ███ RESET",
    ""
]

# Design 7: Large Block Letters (Most Impressive)
design7 = [
    "",
    "COLOR███    ███ ███    ██ ██ ██████   ██████  ███████RESET",
    "COLOR██ █  █ ██ ████   ██ ██ ██   ██ ██    ██ ██     RESET",
    "COLOR██  ██  ██ ██ ██  ██ ██ ██████  ██    ██ ███████RESET",
    "COLOR██      ██ ██  ██ ██ ██ ██   ██ ██    ██      ██RESET",
    "COLOR██      ██ ██   ████ ██ ██████   ██████  ███████RESET",
    ""
]

# Design 8: Stylized with Decorations (RECOMMENDED)
design8 = [
    "",
    "                    COLOR╔═══════════════════════════════╗RESET",
    "                    COLOR║  ╦ ╦╔╗╔╦╔╗ ╔═╗╔═╗  {version}  ║RESET",
    "                    COLOR║  ║ ║║║║║╠╩╗║ ║╚═╗           ║RESET", 
    "                    COLOR║  ╚═╝╝╚╝╩╚═╝╚═╝╚═╝           ║RESET",
    "                    COLOR╚═══════════════════════════════╝RESET",
    ""
]

# Main execution
if __name__ == "__main__":
    print(f"\n{Colors.BOLD}{Colors.CYAN}=== unibos ASCII Art Logo Designs ==={Colors.RESET}")
    print(f"{Colors.DIM}Displaying different logo options for the splash screen{Colors.RESET}")
    
    # Show all designs
    print_design("Design 1: Block Style (Modern, Bold)", design1)
    print_design("Design 2: Double-line Box Drawing", design2)
    print_design("Design 3: 3D Shadow Effect (Most Impressive)", design3)
    print_design("Design 4: Simple ASCII (Cross-platform)", design4)
    print_design("Design 5: Minimalist Style", design5)
    print_design("Design 6: Banner Style with Shading", design6)
    print_design("Design 7: Large Block Letters", design7)
    print_design("Design 8: Stylized with Box (Clean)", design8)
    
    # Show recommended implementation
    print(f"\n{Colors.BOLD}{Colors.CYAN}=== RECOMMENDED IMPLEMENTATION ==={Colors.RESET}")
    print(f"\n{Colors.YELLOW}For the best visual impact, I recommend Design 3 (3D Shadow Effect).{Colors.RESET}")
    print(f"{Colors.YELLOW}It's large, impressive, clearly readable, and works well in orange.{Colors.RESET}")
    
    print(f"\n{Colors.BOLD}Implementation code for main.py:{Colors.RESET}\n")
    
    print('''    # ASCII art - Large and impressive unibos logo
    logo_art = [
        f"",
        f"{Colors.ORANGE}██╗   ██╗███╗   ██╗██╗██████╗  ██████╗ ███████╗{Colors.RESET}",
        f"{Colors.ORANGE}██║   ██║████╗  ██║██║██╔══██╗██╔═══██╗██╔════╝{Colors.RESET}",
        f"{Colors.ORANGE}██║   ██║██╔██╗ ██║██║██████╔╝██║   ██║███████╗{Colors.RESET}",
        f"{Colors.ORANGE}██║   ██║██║╚██╗██║██║██╔══██╗██║   ██║╚════██║{Colors.RESET}",
        f"{Colors.ORANGE}╚██████╔╝██║ ╚████║██║██████╔╝╚██████╔╝███████║{Colors.RESET}",
        f"{Colors.ORANGE} ╚═════╝ ╚═╝  ╚═══╝╚═╝╚═════╝  ╚═════╝ ╚══════╝{Colors.RESET} {Colors.YELLOW}{version}{Colors.RESET}",
        f""
    ]
    
    # Update logo_width for centering
    logo_width = 48  # Width of the new logo''')
    
    print(f"\n\n{Colors.BOLD}Alternative clean design (Design 1):{Colors.RESET}\n")
    
    print('''    # ASCII art - Bold block style unibos logo
    logo_art = [
        f"",
        f"{Colors.ORANGE}██   ██ ███    ██ ██ ██████   ██████  ███████{Colors.RESET}",
        f"{Colors.ORANGE}██   ██ ████   ██ ██ ██   ██ ██    ██ ██     {Colors.RESET}",
        f"{Colors.ORANGE}██   ██ ██ ██  ██ ██ ██████  ██    ██ ███████{Colors.RESET}", 
        f"{Colors.ORANGE}██   ██ ██  ██ ██ ██ ██   ██ ██    ██      ██{Colors.RESET}",
        f"{Colors.ORANGE} ██████  ██   ████ ██ ██████   ██████  ███████{Colors.RESET} {Colors.YELLOW}{version}{Colors.RESET}",
        f""
    ]
    
    # Update logo_width for centering
    logo_width = 46  # Width of the new logo''')
    
    print(f"\n\n{Colors.DIM}Run this script to see all designs in your terminal!{Colors.RESET}\n")