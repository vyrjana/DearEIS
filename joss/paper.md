---
title: DearEIS - A GUI program for analyzing impedance spectra
tags:
- Python
- electrochemistry
- impedance spectroscopy
authors:
- name: Ville Yrjänä
  orcid: 0000-0001-5779-5201
  affiliation: 1
affiliations:
- name: Åbo Akademi University, Faculty of Science and Engineering, Johan Gadolin Process Chemistry Centre, Laboratory of Molecular Science and Engineering, Henriksgatan 2, FI-20500 Turku (Åbo), Finland
  index: 1
bibliography: paper.bib
---


# Summary

Electrochemical impedance spectroscopy (EIS) is a technique that is widely used to characterize the properties of materials used in, e.g., batteries and ion-selective electrodes.
Analyses of the recorded impedance spectra typically involve a data validation step followed by fitting a suitable model to extract quantitative data.
Analyses of the distribution of relaxation times may also be relevant.
DearEIS is a free, open-source, cross-platform program developed for performing such analysis work.
The primary audience for DearEIS is researchers and engineers.
However, the program may also prove useful in the context of, e.g., teaching university-level courses on electrochemistry.


# Statement of need

DearEIS [@deareis] aims to fill a niche that in the author's opinion is currently not filled by other software:

- free and cross-platform to lower the barrier to entry
- open source to maximize extensibility
- support for reading multiple data formats
- capable of performing Kramers-Kronig testing (KK), distribution of relaxation times (DRT) analysis, and equivalent circuit fitting (ECF)
- graphical user interface (GUI) for ease of use
- application programming interface (API) to facilitate batch processing

Several programs that are capable of performing KK, DRT, and/or ECF do already exist but they fail to fulfill at least one of the points listed above.
For example, restrictive licenses and/or digital rights management technologies may prevent distribution of the software or its derivatives to, e.g., colleagues or students.
Some free alternatives do exist (\autoref{tbl:free_alternatives}) though not all of them are open source (\autoref{tbl:license_comparison}) and in some cases they are not straightforward to use.
The software included in \autoref{tbl:free_alternatives} meet to varying degrees the desired qualities listed above (\autoref{tbl:license_comparison} and \ref{tbl:feature_comparison}).
Thus, there was an impetus to develop DearEIS.

The core functionality (circuits, KK, DRT, ECF, etc.) is implemented as a separate package called pyimpspec [@pyimpspec].
DearEIS provides a GUI, which is implemented using Dear PyGui [@dearpygui], and an API wrapper for pyimpspec's API.
The inclusion of both a GUI and an API makes DearEIS suitable for people of varying technical abilities and needs.
These two interfaces also facilitate the use of hybrid workflows where tasks that are easier to do manually can be performed using the GUI (e.g., iterative development of equivalent circuits or basic composition of figures) while other tasks can be automated using Python scripts (e.g., batch processing results to generate publication-ready tables and/or figures).

\pagebreak


Table: Free software that are available for analyzing impedance spectra.
$\rm ^1$pyimpspec is a dependency of DearEIS.
$\rm ^2$Requires MATLAB and the Optimization Toolbox.
\label{tbl:free_alternatives}

-------------------------------------------------------
Name                        Reference
--------------------------- ---------------------------
DearEIS/pyimpspec$\rm ^1$   @deareis/@pyimpspec

DRT-python-code             @kulikovsky2020pem

DRTtools$\rm ^2$            @wan2015influence

EIS Spectrum Analyser       @eissa

Elchemea Analytical         @elchemea

impedance.py                @murbach2020impedance

Kramers-Kronig Test         @kkwin

LEVMW/LEVM                  @levm

Lin-KK Tool                 @linkk

pyDRTtools                  @wan2015influence

PyEIS                       @knudsen2019pyeis

-------------------------------------------------------


Table: Comparison of source code availability, licenses, and supported major platforms of the software included in \autoref{tbl:free_alternatives}.
Some of the software may work on additional platforms, e.g., by using a compatibility layer or emulator.
$\rm ^1$The Apache License version 2.0 (APLv2), the GNU General Public License version 3.0 (GPLv3), and the MIT license (MIT).
\label{tbl:license_comparison}

-------------------------------------------------------------------------------------
Name                   Source available   License$\rm ^1$ Platform(s)
---------------------  ------------------ --------------- ---------------------------
DearEIS/pyimpspec      Yes (Python)       GPLv3           Linux, MacOS, Windows

DRT-python-code        Yes (Python)       GPLv3           Linux, MacOS, Windows

DRTtools               Yes (MATLAB)       MIT             Linux, MacOS, Windows

EIS Spectrum Analyser                                     Windows

Elchemea Analytical    Yes (Perl)         GPLv3           Linux

impedance.py           Yes (Python)       MIT             Linux, MacOS, Windows

Kramers-Kronig Test                                       Windows

LEVMW/LEVM             Yes (Fortran)                      Windows/MS-DOS

Lin-KK Tool                                               Windows

pyDRTtools             Yes (Python)       MIT             Linux, MacOS, Windows

PyEIS                  Yes (Python)       APLv2           Linux, MacOS, Windows

-------------------------------------------------------------------------------------


Table: Comparison of some key features currently available in the software included in \autoref{tbl:free_alternatives}.
$\rm ^1$Kramers-Kronig testing.
$\rm ^2$Distribution of relaxation times analysis.
$\rm ^3$Equivalent circuit fitting.
$\rm ^4$Application programming interface (API), command-line interface (CLI), or graphical user interface (GUI).
$\rm ^5$Script that temporarily displays figures.
$\rm ^6$Web interface to local or remote instance.
\label{tbl:feature_comparison}

-----------------------------------------------------------------------------
Name                   KK$\rm ^1$  DRT$\rm ^2$ ECF$\rm ^3$  Interface(s)$\rm ^4$
---------------------  ----------- ----------- -----------  -----------------
DearEIS/pyimpspec      Yes         Yes         Yes          GUI & API/API

DRT-python-code                    Yes                      GUI$\rm ^5$

DRTtools                           Yes                      GUI

EIS Spectrum Analyser  Yes                     Yes          GUI

Elchemea Analytical                            Yes          GUI$\rm ^6$ & CLI

impedance.py           Yes                     Yes          API

Kramers-Kronig Test    Yes                                  GUI

LEVMW/LEVM             Yes         Yes         Yes          GUI/CLI

Lin-KK Tool            Yes                                  GUI

pyDRTtools                         Yes                      GUI

PyEIS                  Yes                     Yes          API

-----------------------------------------------------------------------------

\pagebreak


# Acknowledgments

Some parts of pyimpspec and, by extension, DearEIS are based on code from DRT-python-code, Elchemea Analytical, impedance.py, and pyDRTtools.
See the LICENSES folders in the GitHub repositories for more information.
The author would like to thank Wenyang Xu for providing feedback and help with testing during development.
The financial support of the author's doctoral studies during the development of pyimpspec and DearEIS by Svenska Litteratursällskapet i Finland, Åbo Akademi University, and Suomen Kulttuurirahasto is gratefully acknowledged.


# References
