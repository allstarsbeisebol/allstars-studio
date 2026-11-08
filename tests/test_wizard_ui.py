"""Valida a navegação guiada no HTML, sem navegador, rede ou APIs pagas."""
from html.parser import HTMLParser
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
HTML=(ROOT/"public/index.html").read_text(encoding="utf-8")
class NavigationStructure(HTMLParser):
    VOID={"area","base","br","col","embed","hr","img","input","link","meta","param","source","track","wbr"}
    def __init__(self):
        super().__init__()
        self.stack=[]
        self.ids={}
        self.screen_ids={}
        self.duplicates=[]
        self.under={}
    def handle_starttag(self,tag,attrs):
        props=dict(attrs)
        node_id=props.get("id")
        if node_id:
            if node_id in self.ids:self.duplicates.append(node_id)
            self.ids[node_id]=props
            self.under[node_id]=[a[1] for a in self.stack if a[1]]
            if props.get("data-studio-screen"):
                self.screen_ids[node_id]=props["data-studio-screen"]
        if tag not in self.VOID:self.stack.append((tag,node_id))
    def handle_startendtag(self,tag,attrs):
        self.handle_starttag(tag,attrs)
        if tag not in self.VOID:self.handle_endtag(tag)
    def handle_endtag(self,tag):
        for i in range(len(self.stack)-1,-1,-1):
            if self.stack[i][0]==tag:
                self.stack=self.stack[:i]
                return

class WizardUiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parser=NavigationStructure()
        cls.parser.feed(HTML)
        cls.code=HTML.split('<script type="module">',1)[1].split('</script>',1)[0]
    def test_single_interaction_for_each_id(self):
        self.assertFalse(self.parser.duplicates,"IDs repetidos: "+str(self.parser.duplicates))
    def test_one_screen_at_a_time(self):
        expected={
         "overview":"home","options":"editor","confirm-panel":"confirm",
         "progress":"progress","art-review":"art",
         "downloads":"result","library":"library","alert-settings":"alerts"
        }
        for element,screen in expected.items():
            self.assertEqual(self.parser.screen_ids.get(element),screen)
    def test_content_and_references_are_isolated(self):
        required={
          "content-type":"wizard-pane-content",
          "subject":"wizard-pane-content",
          "wizard-content-next":"wizard-pane-content",
          "reference-links-text":"wizard-pane-references",
          "reference-text":"wizard-pane-references",
          "wizard-references-skip":"wizard-pane-references",
          "wizard-references-back":"wizard-pane-references",
          "review":"wizard-pane-references",
        }
        for element,pane in required.items():
            self.assertIn(pane,self.parser.under.get(element,[]),element)
        self.assertIn("confirm-panel",self.parser.under.get("generate",[]))
        self.assertIn("art-review",self.parser.under.get("art-approve",[]))
    def test_menu_and_recovery_controls_present(self):
        for element in (
          "home-create","home-continue","home-library",
          "wizard-progress","wizard-steps","wizard-current-number",
          "wizard-progress-home","wizard-art-home","wizard-art-progress",
          "mobile-menu-toggle","draft-status","overview-pending"
        ):
            self.assertIn(element,self.parser.ids)
        self.assertIn("const WIZARD_VIEW_KEY=",self.code)
        self.assertIn("function showWizardScreen(",self.code)
        self.assertIn("function continuePending(",self.code)
        self.assertIn("routeWizardScreen(requested,pending)",(ROOT/"public/wizard.js").read_text())
    def test_no_duplicate_issue_on_return(self):
        self.assertIn("if(pending){continuePending();return;}",self.code)
        self.assertIn("pending=data.request_id;",self.code)
        self.assertIn("showWizardScreen('progress')",self.code)
        self.assertIn("showWizardScreen('confirm')",self.code)
        self.assertIn("showWizardScreen('result')",self.code)
        self.assertIn("data-wizard-go=\"library\"",HTML)
    def test_still_requires_art_approval(self):
        self.assertIn("submitArtAction('approve')",self.code)
        self.assertIn("art-revision-label",HTML)
        self.assertIn("external-image-drop",HTML)
        self.assertIn("prompt_imagem_ia.txt",self.code)
        self.assertIn("Nenhum vídeo foi produzido ainda",self.code)

if __name__=="__main__":unittest.main()
