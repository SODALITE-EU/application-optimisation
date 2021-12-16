/*
  This is a ROOT script (https://root.cern.ch/). Please visit the website to get help on how to install ROOT on your system.
  Then you can run this script with

  > root analysis.cpp

  The script execution will read the data from the CVS files as listed in filenames variable.
  Then, the script execution will show and fit the values with the Amdahl's law.
  The max value of the fit can be adjusted via max_fit_nranks variable.

  Finally, the Amdahl's law model is used to derive the values of the points > max_fit_nranks.
*/

string filepath = "../results/";
auto filenames = {
		  "Case_prep-3_Segments-4mm-2mm___Case_prep-3_Segments_4mm_2mm-DM_SOUS_DOMAINE_METIS_PETSC.com___MPICH.csv",
		  "Case_prep-3_Segments-4mm-2mm___Case_prep-3_Segments_4mm_2mm-DM_SOUS_DOMAINE_METIS_PETSC.com___OpenMPI.csv"
};

double max_fit_nranks = 6;

int analysis_amdahl()
{
  // Set graphical style
  gROOT->SetStyle("Plain");
  gStyle->SetTitleX(0.5);
  gStyle->SetTitleAlign(23);
  gStyle->SetTitleBorderSize(0);

  std::cout.setf(std::ios_base::fixed, std::ios_base::floatfield);
  std::cout.precision(3);

  for (auto filename : filenames) {
    cout << "Read file: " << filepath+filename << std::endl;
    // Read CSV data
    auto data = ROOT::RDF::MakeCsvDataFrame(filepath+filename);
    auto distname = data.Take<string>("mpidist")->front();

    // Add efficiency column
    auto timeref = data.Take<double>("time")->front();
    auto formula = TString::Format("%f/time/nranks", timeref);
    auto efficiency = data.Define("efficiency", formula.Data());

    // Plot
    auto c1 = new TCanvas(distname.c_str(), distname.c_str(), 200, 10, 1000, 1000);
    c1->SetTickx();
    c1->SetTicky();
    c1->SetGridx();
    c1->SetGridy();
    c1->SetLeftMargin(0.13);
    c1->SetBottomMargin(0.13);

    auto gr = efficiency.Graph("nranks", "efficiency");
    gr->SetTitle(distname.c_str());
    gr->GetXaxis()->SetTitle("# MPI ranks");
    gr->GetXaxis()->CenterTitle();
    gr->GetXaxis()->SetTitleOffset(1.4);
    gr->GetYaxis()->SetTitle("Parallel Efficiency");
    gr->GetYaxis()->CenterTitle();
    gr->GetYaxis()->SetTitleOffset(1.4);
    gr->SetMarkerStyle(21);
    gr->SetMarkerColor(kRed);
    gr->SetMarkerSize(2);
    gr->GetXaxis()->SetLimits(0, efficiency.Max("nranks").GetValue());
    gr->DrawClone("AP");
    gr->SetMinimum(0);
    gr->SetMaximum(1.2);

    // Fits
    auto amdahl_model = [](double* xs, double* ps) {
			  return 1/(xs[0]*(1-ps[0])+ps[0]);
			};
    auto fcn = new TF1("fcn", amdahl_model, 0, 1, 1);
    fcn->SetParName(0, "F");
    fcn->SetParameter(0, 0.5);
    fcn->SetParLimits(0, 0, 1);
    fcn->SetRange(1, max_fit_nranks);
    gr->Fit(fcn->GetName(), "R");
    fcn->Draw("same");

    // Draw statistics
    TPaveText *pt = new TPaveText(.5,.8-.05*fcn->GetNpar(),.85,.85, "ndc");
    for (int ipar=0; ipar!=fcn->GetNpar(); ++ipar) {
    pt->AddText(TString::Format("%s = %.4f #pm %.4f", fcn->GetParName(ipar),
				fcn->GetParameter(ipar),
				fcn->GetParError(ipar)));
    }
    pt->Draw();

    // Draw test_marks via the performance model
    int npoints = 0;
    auto test_marks = new TGraph();
    for (auto nranks : efficiency.Take<Long64_t>("nranks")) {
      if (nranks>max_fit_nranks) {
	test_marks->SetPoint(npoints, nranks, fcn->Eval(nranks));
	npoints++;
      }
    }
    test_marks->SetMarkerStyle(20);
    test_marks->SetMarkerSize(1.5);
    test_marks->Draw("P");
  }

  return 0;

}
