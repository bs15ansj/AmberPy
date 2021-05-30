# AmberPy

AmberPy is a tool for performing molecular dynamics simulations using Amber on the Arc High Performance Cluster (HPC) at The University of Leeds.

## Description

AmberPy makes perfoming molecular dynamics simulations simple. To run, all you need is access to a Linux machine and an account on the Arc. Setting up and running a simulation can be done wth a command as simple as:
```
james [pdb_file]
```

Alternatively, AmberPy can be used as a python library to perform simulations using a script as simple as:
```
from amberpy.experiments import ProteinSimulation
p = ProteinSimulation([pdb_file])
p.make_system()
p.add_minimisation_step()
p.add_equilibration_step()
p.add_production_step()
p.run()
```
This tool is intended to be used by students and staff at the University of Leeds, since an account on Arc is required. In the future, we hope to extend this to users with access to other HPCs. 

## Documentation

View the full documentation at amberpy.readthedocs.io.

## References

Gebbie-Rayet, J, Shannon, G, Loeffler, H H and Laughton, C A 2016 Longbow: A Lightweight Remote Job Submission Tool. Journal of Open Research Software, 4: e1, DOI: http://dx.doi.org/10.5334/jors.95

D.A. Case, H.M. Aktulga, K. Belfon, I.Y. Ben-Shalom, S.R. Brozell, D.S. Cerutti, T.E. Cheatham, III, V.W.D. Cruzeiro, T.A. Darden, R.E. Duke, G. Giambasu, M.K. Gilson, H. Gohlke, A.W. Goetz, R. Harris, S. Izadi, S.A. Izmailov, C. Jin, K. Kasavajhala, M.C. Kaymak, E. King, A. Kovalenko, T. Kurtzman, T.S. Lee, S. LeGrand, P. Li, C. Lin, J. Liu, T. Luchko, R. Luo, M. Machado, V. Man, M. Manathunga, K.M. Merz, Y. Miao, O. Mikhailovskii, G. Monard, H. Nguyen, K.A. O’Hearn, A. Onufriev, F. Pan, S. Pantano, R. Qi, A. Rahnamoun, D.R. Roe, A. Roitberg, C. Sagui, S. Schott-Verdugo, J. Shen, C.L. Simmerling, N.R. Skrynnikov, J. Smith, J. Swails, R.C. Walker, J. Wang, H. Wei, R.M. Wolf, X. Wu, Y. Xue, D.M. York, S. Zhao, and P.A. Kollman (2021), Amber 2021, University of California, San Francisco. 

## Authors

Alex St John (bs15ansj@leeds.ac.uk)

## Help

This package is currently in early development and so issues may be present. If you have any queries at all please don't hesitate to contact the author. 

## Version History

* 0.0.1
    * Initial Release

## License

This project is licensed under the MIT License - see the LICENSE file for details
