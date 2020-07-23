
/*
  This is a ROOT script (https://root.cern.ch/). Please visit the website to get help on how to install ROOT on your system.
  Then you can run this script with

  > root analysis.cpp

  The script execution will read the data from the file 'daint.txt' (you can change the name of the file by changing the
  variable filename). The format of the file is:

  <header of the columns>
  <values per columns>

  A value can be skipped with the '-1' value, e.g.

  #nodes #ppn #procs HPL_Tflops RandomlyOrderedRingBandwidth_GBytes StarSTREAM_Triad b_eff_io hpcg
  1 1 1 0.0256688 -1 15.874 652.947 1.56042
  1 2 2 0.0555889 12.7783 17.669 864.584 -1
  1 36 36 0.544872 1.09368 2.45694 907.140 17.1878

  Then, the script execution will show and fit the values, including the combined model.
  Finally, the model will be applied to given values (see varaible xp at the beginning of the script).
  Monte Carlo method is used to extract the errors.
 */

// Input values
const char* filename = "daint.txt";

// Value to derive
const std::vector<double> xp {1, 10*36, 20*36};

// Components must be global defined
TF1 *fn_hpl(0), *fn_mpibw(0), *fn_membw(0), *fn_iobw(0);

std::vector<std::string> headers;
std::map<int, std::vector<double>> vals;

TF1* draw(int icol, bool scale, const char* name, const char* title, TF1 *fcn = nullptr) {
  std::cout << std::endl;
  std::cout << "***** " << headers[icol] << " *****" << std::endl;
  std::cout << std::endl;

  int ii = 0;
  int skip = 1;
  double fval = -1;
  bool first = true;
  std::vector<double> xvals, yvals;
  for (auto ncores : vals[2]) {
    double val = vals[icol][ii];
    if (val>0) {
      if (scale) {
	val *= ncores;
      }

      if (fval<0) {
	fval = val;
      }

      if (ii!=1 or first) {
	std::cout << ncores << " " << val/fval << std::endl;
	xvals.push_back(ncores);
	yvals.push_back(val/fval);
      }
      first = false;
    }
    else {
      first = false;
    }
    ii++;
  }

  auto c1 = new TCanvas(name,headers[icol].c_str(),200,10,1000,1000);
  c1->SetTickx();
  c1->SetTicky();
  c1->SetGridx();
  c1->SetGridy();
  auto gr = new TGraph(xvals.size(),&xvals[0],&yvals[0]);
  gr->SetTitle(title);
  gr->GetXaxis()->SetTitle("#cores");
  gr->GetXaxis()->CenterTitle();
  gr->GetXaxis()->SetTitleOffset(1.4);
  gr->GetYaxis()->SetTitle("Speed-up");
  gr->GetYaxis()->CenterTitle();
  gr->GetYaxis()->SetTitleOffset(1.4);
  gr->SetMarkerStyle(21);
  gr->SetMarkerColor(kRed);
  gr->SetMarkerSize(2);
  gr->Draw("AP");
  gr->SetMinimum(0);
  gr->GetXaxis()->SetLimits(0, xvals.back());
  if (!fcn) {
    fcn = new TF1(name, "[0]+[1]*x");
    fcn->SetParName(0, ("p0_{"+std::string(title)+"}").c_str());
    fcn->SetParName(1, ("p1_{"+std::string(title)+"}").c_str());
  }
  fcn->SetRange(xvals.front(), xvals.back());
  gr->Fit(fcn->GetName(), "R");
  c1->SetLeftMargin(0.13);
  c1->SetBottomMargin(0.13);
  double ess = 0;
  double tss = 0;
  double mean = gr->GetMean(2);
  for (int iy = 0; iy<yvals.size(); ++iy) {
    ess += TMath::Power(fcn->Eval(xvals[iy])-mean, 2);
    tss += TMath::Power(yvals[iy]-mean, 2);
  }
  TPaveText *pt = new TPaveText(.15,.8-.05*fcn->GetNpar(),.5,.85, "ndc");
  pt->AddText("R2 = "+TString::Format("%.3f", ess/tss));
  for (int ipar=0; ipar!=fcn->GetNpar(); ++ipar) {
    pt->AddText(TString::Format("%s = %.4f #pm %.4f", fcn->GetParName(ipar),
				fcn->GetParameter(ipar),
				fcn->GetParError(ipar)));
  }
  pt->Draw();
  std::cout << "R2 = " << ess/tss << std::endl;
  return fcn;
}

int analysis()
{
  gROOT->SetStyle("Plain");
  gStyle->SetTitleX(0.5);
  gStyle->SetTitleAlign(23);
  gStyle->SetTitleBorderSize(0);
  //  gStyle->SetOptFit(1);
  std::cout.setf(std::ios_base::fixed, std::ios_base::floatfield);
  std::cout.precision(3);

  std::ifstream fdata;
  fdata.open(filename);

  // Read header and values
  std::string tmp;
  int ii = 0;
  while (fdata >> tmp) {

    if (std::isdigit(tmp[0]) or tmp[0]=='-') {
      int icol = ii%headers.size();
      vals[icol].push_back(std::stod(tmp));
      ii++;
    }
    else {
      headers.push_back(tmp);
    }
  }
  fdata.close();

  // Print values for checking
  for (auto col : headers) {
    std::cout << col << " ";
  }
  std::cout << std::endl;
  ii = 0;
  while (ii<vals[0].size()) {
    for (auto col : vals) {
      std::cout << col.second[ii] << " ";
    }
    std::cout << std::endl;
    ii++;
  }

  // Fits
  fn_hpl = draw(3, false, "hpl", "HPL");
  auto l_pol_two = [](double* xs, double* ps) {
		     if (xs[0]<(ps[2]-ps[0])/(ps[1]-ps[3]))
		       return ps[0]+ps[1]*xs[0];
		     else
		       return ps[2]+ps[3]*xs[0];
		   };
  auto pol_two = new TF1("mpibw", l_pol_two, 0, 1, 4);
  pol_two->SetParName(0, "p0_{MPI BW}");
  pol_two->SetParameter(0, 1);
  pol_two->SetParName(1, "p1_{MPI BW}");
  pol_two->SetParameter(1, -0.005);
  pol_two->SetParLimits(1, -1, 0);
  pol_two->SetParName(2, "q0_{MPI BW}");
  pol_two->SetParameter(2, 0.5);
  pol_two->SetParName(3, "q1_{MPI BW}");
  pol_two->SetParameter(3, 0.004);
  pol_two->SetParLimits(3, 0, 1);
  fn_mpibw = draw(4, true, "mpibw", "MPI BW", pol_two);
  std::cout << pol_two->GetName() << " turning point = "
	    << (pol_two->GetParameter(3)-pol_two->GetParameter(1))/(pol_two->GetParameter(0)-pol_two->GetParameter(2))
	    << std::endl;

  fn_membw = draw(5, true, "membw", "MEM BW");
  fn_iobw = draw(6, false, "iobw", "IO BW");

  // Fit model, linear combination
  auto l_model = [&](double* xs, double* ps) {
		   return ps[0]*fn_hpl->Eval(xs[0])+
		     ps[1]*fn_mpibw->Eval(xs[0])+
		     ps[2]*fn_membw->Eval(xs[0])+
		     (1-ps[0]-ps[1]-ps[2])*fn_iobw->Eval(xs[0]);
		 };
  auto model = new TF1("model", l_model, 0, 1, 3);
  model->SetParName(0, "f_{HPL}");
  model->SetParameter(0, 0.1);
  //  model->SetParLimits(0, -2, 2);
  model->SetParName(1, "f_{MPI BW}");
  model->SetParameter(1, 0.1);
  //  model->SetParLimits(1, -2, 2);
  model->SetParName(2, "f_{MEM BW}");
  model->SetParameter(2, 0.1);
  //  model->SetParLimits(2, -5, 5);

  //  int fixpar = fcomb->GetNumberFreeParameters();
  //  for (int ipar=3; ipar<fixpar; ++ipar) {
  //    fcomb->FixParameter(ipar, fcomb->GetParameter(ipar));
  //  }

  auto fn_hpl_comb = draw(7, false, "HPCG", "HPCG", model);

  auto apply_model = [&](double vk, double ck, double cX) -> double {
		       return vk*(model->Eval(1)/model->Eval(ck))*model->Eval(cX);
		     };

  // Derive values

  std::vector<std::pair<double, double>> start_vals_errs;
  // Save start values
  for (int ipar=0; ipar!=model->GetNpar(); ++ipar) {
    start_vals_errs.push_back(std::make_pair(model->GetParameter(ipar), model->GetParError(ipar)));
  }

//  auto h1 = new TH1F("h1","h1",100,10,300);

  std::vector<double> mean(xp.size(), 0.), mean2(xp.size(), 0.);
  const int nps = 1000*model->GetNpar();
  for (int np=0; np!=nps; ++np) {
    // Randomize
    for (int ipar=0; ipar!=model->GetNpar(); ++ipar) {
      model->SetParameter(ipar, gRandom->Gaus(start_vals_errs[ipar].first, start_vals_errs[ipar].second));
    }
    for (int ix = 0; ix!=xp.size(); ++ix) {
      // Use [0] entry (single core) as reference
      double val = apply_model(vals[7][0],vals[2][0],xp[ix]);
      mean[ix] += val;
      mean2[ix] += val*val;
      //    h1->Fill(val);
    }
  }

  // Restore start values
  for (int ipar=0; ipar!=model->GetNpar(); ++ipar) {
    model->SetParameter(ipar, start_vals_errs[ipar].first);
    model->SetParError(ipar, start_vals_errs[ipar].second);
  }

  std::cout << std::endl;
  for (int ix = 0; ix!=xp.size(); ++ix) {
    //  h1->Draw();
    mean2[ix] /= nps;
    mean[ix] /= nps;

    std::cout << "#cores " << std::setw(4) << int(xp[ix])
	      << " \t mean " << std::setw(8) << mean[ix]
	      << " +/- " << TMath::Sqrt(mean2[ix]-mean[ix]*mean[ix])
	      << " \t model value " << apply_model(vals[7][0],vals[2][0],xp[ix])
	      << std::endl;
  }

  return 0;
}
