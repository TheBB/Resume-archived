(TeX-add-style-hook
 "resume"
 (lambda ()
   (TeX-add-to-alist 'LaTeX-provided-class-options
                     '(("res" "line" "margin")))
   (TeX-add-to-alist 'LaTeX-provided-package-options
                     '(("nth" "super") ("inputenc" "utf8")))
   (TeX-run-style-hooks
    "latex2e"
    "res"
    "res10"
    "charter"
    "graphicx"
    "wrapfig"
    "nth"
    "inputenc")
   (TeX-add-symbols
    "zh")
   (LaTeX-add-environments
    "absnopagebreak"))
 :latex)

