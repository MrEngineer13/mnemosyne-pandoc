import subprocess

from mnemosyne.libmnemosyne.filter import Filter
from mnemosyne.libmnemosyne.plugin import Plugin


def convert(string, source='markdown', extensions=None, target='html',
            pandoc='/usr/bin/pandoc', extra_args=None):
    """Convert text from one format to another using Pandoc.

    Parameters
    ----------
    string: str
      The text to convert
    source: str
      The format to convert from
    extensions: list[str]
      A list of pandoc format extensions
    target: str
      The format to convert to
    pandoc: str
      Path to the Pandoc binary
    extra_args: list[str]
      A list of additional arguments
    """
    if extensions is not None:
        source = source + ''.join(extensions)

    extra_args = extra_args or []
    args = [pandoc, '--from=' + source,
            '--to=' + target] + list(extra_args)

    p = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    result, err = p.communicate(bytes(string, 'utf-8'))
    string_res = result.decode()
    return string_res
    
    

def _unescape_braces(string):
    return string.replace('%7B', '{').replace('%7D', '}')


def md_to_html(string, extensions=['-tex_math_dollars',
                                    '+tex_math_single_backslash',
                                    '+tex_math_double_backslash']):
    """Convert markdown to html."""
    return _unescape_braces(convert(string, source='markdown',
                                    extensions=extensions, target='html',
                                    extra_args = ['--section-divs',
                                                  '--mathjax']))


def md_to_tex(string, extensions=['+tex_math_single_backslash',
                                   '+tex_math_double_backslash']):
    """Convert markdown to latex."""
    return convert(string, source='markdown',
                   extensions=extensions,
                   target='latex')


def is_latex_card(card):
    """Should the current card be formatted in latex?"""
    return 'latex' in [tag.name for tag in card.tags]


class Pandoc(Filter):

    def run(self, text, card, fact_key, **render_args):
        if is_latex_card(card):
            pre = r'<latex>\small{'
            post = r'}</latex>'
            return pre + md_to_tex(text) + post
        else:
            return md_to_html(text)


class PandocPlugin(Plugin):

    name = "Pandoc"
    description = "Use pandoc markdown for cards."
    components = [Pandoc]

    def activate(self):
        Plugin.activate(self)
        self.render_chain("default").\
            register_filter(Pandoc, in_front=True)
        # self.render_chain("card_browser").\
        #     register_filter(Pandoc, in_front=True)

    def deactivate(self):
        Plugin.deactivate(self)
        self.render_chain("default").\
            unregister_filter(Pandoc)
        # self.render_chain("card_browser").\
        #     unregister_filter(Pandoc)


# Register plugin.
from mnemosyne.libmnemosyne.plugin import register_user_plugin
register_user_plugin(PandocPlugin)
