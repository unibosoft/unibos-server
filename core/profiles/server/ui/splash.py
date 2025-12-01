"""
UNIBOS Server Profile Splash Screen

!! BU DOSYAYI DÜZENLEME !!
Bu dosya sadece merkezi splash modülünü re-export eder.
Splash'te değişiklik yapmak için:
  → core/clients/cli/framework/ui/splash.py
"""

# Re-export everything from the central splash module
from core.clients.cli.framework.ui.splash import (
    show_splash_screen,
    show_compact_header,
    get_simple_key,
)

# Also export load_version_info for backwards compatibility
from core.version import __version__, __build__


def load_version_info() -> dict:
    """
    Load version information - uses core.version module directly

    Returns:
        Version info dict
    """
    return {
        'version': f'v{__version__}',
        'build': __build__,
        'build_date': 'unknown',
        'author': 'berk hatirli',
        'location': 'bitez, bodrum, muğla, türkiye, dünya, güneş sistemi, samanyolu, evren'
    }


# Legacy aliases for backwards compatibility
def show_splash():
    """Legacy alias for show_splash_screen"""
    show_splash_screen(quick=True)


def show_header():
    """Legacy alias for show_compact_header"""
    show_compact_header(cli_name="unibos-server")
