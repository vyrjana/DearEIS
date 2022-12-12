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
- name: Åbo Akademi University, Faculty of Science and Engineering, Johan Gadolin Process Chemistry Centre, Laboratory of Molecular Science and Engineering, Turku (Åbo), Finland
  index: 1
bibliography: paper.bib
header-includes:
 \usepackage{tikz}
 \usepackage{graphicx}
 \usepackage{xcolor}
 \newcommand{\su}[1]{$\rm ^#1$}
---


# Summary

Electrochemical impedance spectroscopy (EIS) is a technique that is widely used to characterize the properties of materials used in, e.g., batteries and ion-selective electrodes.
Analyses of the recorded impedance spectra typically involve some preprocessing, data validation, and fitting of a suitable model to extract quantitative data.
Analyses of the distribution of relaxation times may also be relevant and can help with choosing an appropriate model.
DearEIS is a free, open source, cross-platform program developed for performing such analysis work.
The primary audience for DearEIS is researchers and engineers.
However, the program may also prove useful in the context of, e.g., teaching university-level courses on electrochemistry.


\begin{figure}
	\centering
	\begin{tikzpicture}
		\draw[draw=none]
			(0.0cm, 0.0cm) -- 
			(0.0cm, 9.0cm) -- 
			(13.5cm, 9.0cm) -- 
			(13.5cm, 0.0cm) -- 
			(0.0cm, 0.0cm);

		\def\minnodewidth{0.5cm}
		\def\minnodeheight{0.5cm}
		\definecolor{vibrantblue}{HTML}{0077BB}
		\definecolor{vibrantorange}{HTML}{EE7733}
		\tikzstyle{process} = [minimum height=\minnodeheight, fill=vibrantblue, opacity=0.2, text opacity=1.0, align=center]
		\begin{scope}[shift={(1.25cm,6.0cm)}]
			\node (experimental) at (0.25cm, 1.5cm) [draw, minimum height=\minnodeheight, fill=vibrantorange, opacity=0.2, text opacity=1.0, align=center] {Record \\ spectrum};
			\node (preprocessing) at (2.75cm, 1.5cm) [draw, process] {Preprocess \\ data};
			\node (validation) at (5.15cm, 1.5cm) [draw, process] {Validate \\ data};
			\node (fitting) at (7.75cm, 2.5cm) [draw, process] {Fit equivalent circuit};
			\node (drt) at (7.75cm, 0.5cm) [draw, process] {Calculate DRT\su{1}};
			\node (results) at (10.6cm, 1.5cm) [draw, process] {Prepare \\ plots/tables};


			\tikzstyle{arrow} = [line width=0.5mm, ->, >=stealth]
			\tikzstyle{dashedarrow} = [line width=0.5mm, ->, >=stealth, dashed]
			\draw[arrow] (experimental) -- (preprocessing);
			\draw[arrow] (preprocessing) -- (validation);
			\draw[arrow] (validation) |- (fitting);
			\draw[arrow] (validation) |- (drt);
			\draw[dashedarrow] (drt) -- (fitting);
			\draw[dashedarrow] (fitting.north) |- ++(-.75, .45) -| (preprocessing.north);
			\draw[arrow] (fitting) -| (results);
			\draw[arrow] (drt) -| (results);

			\draw[draw=black, line width=0.3mm, dotted]
				(12.00cm,  0.00cm) --
				( 1.50cm,  0.00cm) --
				( 1.50cm,  3.55cm) --
				( 0.57cm, -0.76cm);
			\draw[draw=none, fill=white] (1.4cm, 3.56cm) rectangle ++(0.2cm, 0.14cm);
			\draw[draw=black, line width=0.3mm, dotted]
				( 1.5cm,   3.55cm) --
				(12.00cm,  3.55cm) --
				(12.00cm,  0.00cm) --
				( 9.44cm, -5.74cm);
		\end{scope}
		\node (screenshot) at (6.25cm, 2.75cm) {\includegraphics[height=5cm, keepaspectratio]{figure-abstract.png}};
	\end{tikzpicture}
	\caption{A flowchart of the steps that are typically involved in the process of obtaining and analyzing impedance spectra. The parts of the process that can be performed with DearEIS are highlighted. \su{1}Distribution of relaxation times.}
	\label{fig:abstract}
\end{figure}

\pagebreak


# Statement of need

DearEIS [@deareis] aims to fill a niche that in the author's opinion is currently not filled by other software:

- free and cross-platform to lower the barrier to entry
- open source to maximize extensibility
- support for importing measurement data from multiple data formats
- capable of performing Kramers-Kronig testing (KK), distribution of relaxation times (DRT) analysis, and equivalent circuit fitting (ECF)
- graphical user interface (GUI) for ease of use
- application programming interface (API) to facilitate batch processing

The core functionality (circuits, KK, DRT, ECF, etc.) of DearEIS is implemented as a separate package called pyimpspec [@pyimpspec].
DearEIS provides a GUI, which is implemented using Dear PyGui [@dearpygui], and an API wrapper for pyimpspec's API.
The inclusion of both a GUI and an API makes DearEIS suitable for people of varying technical abilities and needs.
These two interfaces also facilitate the use of hybrid workflows where tasks that are easier to do manually can be performed using the GUI (e.g., iterative development of equivalent circuits or basic composition of figures) while other tasks can be automated using Python scripts (e.g., batch processing results to generate publication-ready tables and/or figures).
There are several examples (\autoref{tbl:alternatives}) of software capable of performing KK, DRT, and/or ECF but they all fail to fulfill at least one of the points listed above.
Thus, there was an impetus to develop DearEIS.


Table: Examples of software that are available for analyzing impedance spectra.
\su{1}Requires MATLAB and the Optimization Toolbox.
\su{2}pyimpspec is a dependency of DearEIS.
\label{tbl:alternatives}

-------------------------------------------------------------
Name                   Reference or company
---------------------- --------------------------------------
Aftermath              Pine Research Instrumentation, Inc.

**DearEIS**            **@deareis**

DRT-python-code        @kulikovsky2020pem

DRTtools\su{1}         @wan2015influence

EC-Lab                 BioLogic Science Instruments SAS

Echem Analyst          Gamry Instruments, Inc.

EIS Spectrum Analyser  @eissa

Elchemea Analytical    @elchemea

impedance.py           @murbach2020impedance

IviumSoft              Ivium Technologies BV

Kramers-Kronig Test    @kkwin

LEVM/LEVMW             @levm

Lin-KK Tool            @linkk

Nova                   Metrohm AG

PSTrace                PalmSens BV

pyDRTtools             @wan2015influence

PyEIS                  @knudsen2019pyeis

pyimpspec\su{2}        @pyimpspec

RelaxIS                rhd instruments GmbH & Co. KG

Zahner Analysis        Zahner-Elektrik GmbH & Co. KG

ZView                  Scribner Associates, Inc.

-------------------------------------------------------


Some of the other software listed in \autoref{tbl:alternatives} are available for free though they are not necessarily also open source (\autoref{tbl:license_comparison}).
For example, the source code is not publicly available for EIS Spectrum Analyzer, Kramers-Kronig Test, and Lin-KK Tool.
The source code for LEVM/LEVMW is included with the binaries, but the source code is not distributed under an open source license.
DRTtools requires the user to have licenses for MATLAB and its Optimization Toolbox package, which adds a financial barrier to its use.
Fortunately, a Python-based port called pyDRTtools is available.
Several of these free software support multiple platforms.


Table: Comparison of source code availability, applicable open source license(s) if the source code is available, and supported major platforms of the software included in \autoref{tbl:alternatives}.
\su{1}The Apache License version 2.0 (APLv2), the GNU General Public License version 3.0 (GPLv3), and the MIT license (MIT).
\su{2}May also work on other platforms with the help of a compatibility layer or an emulator.
\su{3}pyimpspec is a dependency of DearEIS.
\su{4}Separate Python package that interacts with the main program [@zahner].
\label{tbl:license_comparison}

--------------------------------------------------------------------------------
Name                   Source available     License\su{1} Platform(s)\su{2}
---------------------- -----------------    ------------- ----------------------     
Aftermath                                                 Windows

**DearEIS**            **Yes (Python)**     **GPLv3**     **Linux, MacOS, Windows**

DRT-python-code        Yes (Python)         GPLv3         Linux, MacOS, Windows

DRTtools               Yes (MATLAB)         MIT           Linux, MacOS, Windows

EC-Lab                                                    Windows

Echem Analyst                                             Windows

EIS Spectrum Analyser                                     Windows

Elchemea Analytical    Yes (Perl)           GPLv3         Linux

impedance.py           Yes (Python)         MIT           Linux, MacOS, Windows

IviumSoft                                                 Windows

Kramers-Kronig Test                                       Windows

LEVM/LEVMW             Yes (Fortran)        Not specified MS-DOS/Windows

Lin-KK Tool                                               Windows

Nova                                                      Windows

PSTrace                                                   Windows

pyDRTtools             Yes (Python)         MIT           Linux, MacOS, Windows

PyEIS                  Yes (Python)         APLv2         Linux, MacOS, Windows

pyimpspec\su{3}        Yes (Python)         GPLv3         Linux, MacOS, Windows

RelaxIS                                                   Windows

Zahner Analysis        Yes (Python)\su{4}   MIT\su{4}     Linux, MacOS, Windows

ZView                                                     Windows

--------------------------------------------------------------------------------


Most instrument manufacturers bundle their instruments with software that can be used to analyze impedance spectra and a few third-party companies also sell software for this purpose (\autoref{tbl:license_comparison}).
These two types of software are typically closed source and not publicly available for download (e.g., requiring the purchase of a license or registration of an instrument when making an account).
Trial versions with some limitations (e.g., an inability to save results) may be publicly available in some cases.
Restrictive licenses and/or digital rights management technologies (e.g., the USB dongle or the online verification required by RelaxIS) may limit or even prevent distribution of the software to, e.g., colleagues or students.
The commercial software in \autoref{tbl:license_comparison} only support Windows, with the exception of Zahner Analysis

In terms of key functionality, RelaxIS is the most similar alternative to DearEIS with LEVM/LEVMW as a close second (\autoref{tbl:feature_comparison}).
However, RelaxIS is a closed-source, commercial product, which introduces a financial barrier to entry, and it officially only supports Windows.
LEVM/LEVMW is, as was mentioned earlier, a free though not truly open source alternative.
The software officially supports MS-DOS/Windows but may also work natively on other platforms provided that a compatible Fortran compiler is available.
There is a rather steep learning curve associated with using LEVM and its CLI directly, particularly regarding the process of preparing the input files, despite the rather comprehensive manual that is included.
LEVMW greatly simplifies this process, though some may find its GUI not intuitive to use by modern standards.


Table: Comparison of some key features currently available in the software included in \autoref{tbl:alternatives}.
\su{1}Kramers-Kronig testing.
\su{2}Distribution of relaxation times analysis.
\su{3}Equivalent circuit fitting.
\su{4}Application programming interface (API), command-line interface (CLI), or graphical user interface (GUI).
\su{5}Script that temporarily displays figures.
\su{6}Web interface to local or remote instance.
\su{7}pyimpspec is a dependency of DearEIS.
\su{8}Separate Python package that interacts with the main program [@zahner].
\label{tbl:feature_comparison}

--------------------------------------------------------------------------
Name                   KK\su{1}  DRT\su{2}  ECF\su{3}   Interface(s)\su{4}
---------------------  --------- ---------- ----------  ------------------
Aftermath              Yes                  Yes         GUI

**DearEIS**            **Yes**   **Yes**    **Yes**     **GUI, API**

DRT-python-code                  Yes                    GUI\su{5}

DRTtools                         Yes                    GUI

EC-Lab                 Yes                  Yes         GUI

Echem Analyst          Yes                  Yes         GUI, API

EIS Spectrum Analyser  Yes                  Yes         GUI

Elchemea Analytical                         Yes         GUI\su{6}, CLI

impedance.py           Yes                  Yes         API

IviumSoft              Yes                  Yes         GUI

Kramers-Kronig Test    Yes                              GUI

LEVM/LEVMW             Yes       Yes        Yes         CLI/GUI

Lin-KK Tool            Yes                              GUI

Nova                   Yes                  Yes         GUI

PSTrace                                     Yes         GUI, CLI, API

pyDRTtools                       Yes                    GUI

PyEIS                  Yes                  Yes         API

pyimpspec\su{7}        Yes       Yes        Yes         API

RelaxIS                Yes       Yes        Yes         GUI, API

Zahner Analysis        Yes                  Yes         GUI, API\su{8}

ZView                  Yes                  Yes

--------------------------------------------------------------------------


Some of the software listed in \autoref{tbl:feature_comparison} focus on a single aspect of data analysis while most can do both KK and ECF.
DearEIS includes implementations of the linear Kramers-Kronig tests [@boukamp1995linear] and an algorithm for automatically choosing the number of parallel RC circuits [@schonleber2014method].
An alternative implementation of the latter is also included to help with identifying false negatives.
DearEIS uses lmfit [@lmfit] to perform complex non-linear least-squares fitting, which enables the use of different fitting methods (Levenberg-Marquardt, Nelder-Mead, etc.).
A few different weighting options are also available (modulus, proportional, etc.).
A specific combination of fitting method and weighting can be chosen or multiple combinations can be tried in parallel to find a combination that provides the best fit.
The following circuit elements are currently implemented: resistor, capacitor, constant phase element, inductor, modified inductor, Gerischer, Havriliak-Negami, de Levie, Warburg (semi-infinite, finite space, and finite length).
Additional elements may be implemented in the future.
Lower and upper limits can be defined or omitted for any parameters that a circuit element may have.
The parameter values can also be defined as constant values.
Equivalent circuits can be constructed using either a graphical, node-based editor or a circuit description code (CDC).
DearEIS supports a basic CDC syntax as described by Boukamp [@cdc] and an extended syntax that can be used to also define parameter values, parameter limits, and labels for the circuit elements.

Support for DRT analysis is not very common as can be seen in \autoref{tbl:feature_comparison} even though DRT results can be useful in the development of an appropriate equivalent circuit by revealing the number of time constants present in an impedance spectrum.
The shapes of the peaks in the DRT plots can also provide some information about the type of circuit element that could be appropriate to include in an equivalent circuit (e.g., a sharp, symmetrical peak is typical for the type of slightly non-ideal capacitance that a constant phase element is often used for).
However, calculating the DRT from an impedance spectrum is an ill-posed problem, which means that some care must be taken when interpreting the results.
The wrong combination of impedance spectrum, method, and method parameters can result in, e.g., peaks that are actually just artifacts, or broad peaks that should actually be two or more separate peaks.
DearEIS currently includes support for a few methods for performing DRT analyses:

- Tikhonov regularization and radial basis function (or piecewise linear) discretization with or without Bayesian credible intervals, which was implemented in DRTtools and described by @wan2015influence, @ciucci2015analysis, and @effat2017bayesian
- Bayesian Hilbert transform, which was implemented in DRTtools and described by @liu2020bayesian
- Tikhonov regularization and non-negative least-squares fitting, which was implemented in DRT-python-code as an alternative to the original approach that used projected gradient descent and was described by @kulikovsky2020pem
- multi-(RQ)-fit, which was described by @boukamp2015fourier and @boukamp2017analysis

Software that is bundled with instruments often does not support loading measurement data from many file formats, which may limit its use for the analysis of results obtained with other manufacturer's instruments unless plain-text files with character-separated values are supported such as in the case of IviumSoft.
On the other hand, third-party software like RelaxIS and ZView do support loading measurement data from many different file formats including the formats used by many well-known instrument manufacturers.
DearEIS currently supports importing experimental data from file formats used by some instrument manufacturers (e.g., BioLogic, Gamry, and Ivium).
Experimental data that is stored as character-separated values in spreadsheets (`.xlsx` and `.ods`) or plain-text files can also be imported into DearEIS.

Many of the software included in \autoref{tbl:feature_comparison} have functionality beyond those included in that table (e.g., Mott-Schottky analysis is included in RelaxIS).
Even some of the closed-source software have APIs that can be used to, e.g., batch process analyses (e.g., Zahner Analysis) or implement new circuit elements (e.g., RelaxIS).
DearEIS has several features in addition to those that are included in \autoref{tbl:feature_comparison}:

- disabling data points to, e.g., remove outliers
- making corrections to a data set by subtracting a fixed value, an equivalent circuit's impedance response, or another impedance spectrum
- simulating the impedance response of a circuit
- overlaying data sets and/or analysis results in plots, which can also be exported using matplotlib [@matplotlib] as the backend
- copying various data as plain-text to the system clipboard (e.g., the data used to generate a plot as character-separated values, tables of fitted parameters as Markdown, or circuit diagrams as Scalable Vector Graphics)
- an API that can be used for, e.g., batch processing
- new circuit elements can be added by extending pyimpspec

Ultimately, DearEIS provides a unified GUI for various analytical functions that in some cases were previously only available as separate, smaller programs that may or may not have had a GUI.
The barrier to entry should therefore be quite low since DearEIS works on multiple platforms, is freely available, and does not require a highly technically proficient user.
Simultaneously, DearEIS does facilitate more advanced use cases by providing an API.
The open source nature of DearEIS will hopefully ensure that the project can be extended and used far into the future.


\pagebreak

# Acknowledgments

Some parts of pyimpspec and, by extension, DearEIS are based on code from DRT-python-code, Elchemea Analytical, impedance.py, and pyDRTtools.
See the LICENSES folders in the GitHub repositories for more information.
The author would like to thank Wenyang Xu for providing feedback and help with testing during development.
The financial support of the author's doctoral studies during the development of pyimpspec and DearEIS by Svenska Litteratursällskapet i Finland, Åbo Akademi University, and Suomen Kulttuurirahasto is gratefully acknowledged.


# References
