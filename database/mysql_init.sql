-- MySQL dump 10.13  Distrib 8.0.28, for Win64 (x86_64)
--
-- Host: 134.94.73.128    Database: hte_data
-- ------------------------------------------------------
-- Server version	8.0.34-0ubuntu0.22.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Current Database: `hte_data`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `hte_data` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;

USE `hte_data`;

--
-- Table structure for table `ana_icpms_sfc_fitting`
--

DROP TABLE IF EXISTS `ana_icpms_sfc_fitting`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ana_icpms_sfc_fitting` (
  `id_exp_icpms` int NOT NULL COMMENT 'index of icpms experiment',
  `name_isotope_analyte` varchar(45) NOT NULL COMMENT 'name of the analyte used as internalstandard',
  `name_isotope_internalstandard` varchar(45) NOT NULL COMMENT 'name of the isotope used as internalstandard',
  `id_exp_ec_dataset` int NOT NULL COMMENT 'dataset of ec experiments, can be one or multiple id_exp_sfc as defined by exp_ec_datasets_definer',
  `id_fit` int NOT NULL COMMENT 'index of the processed fit. Default = 0, higher if multiple fits have been performed on the same data.',
  `R2adj` float DEFAULT NULL COMMENT 'adjusted R^2 value as goodness of fit',
  `manual_peaks` varchar(254) DEFAULT NULL COMMENT 'manually added peaks during fit routine',
  `fitinput_datapoints_fit_single_peak` int DEFAULT NULL COMMENT 'amount of datapoints to fit single icpms peak during fit routine',
  `fitinput_datapoints_peak_distance` int DEFAULT NULL COMMENT 'amount of datapoints as minimum distance between peaks for auto detect during fit routine',
  `fitinput_prominence` float DEFAULT NULL COMMENT 'prominence to auto detect the peaks during fit routine',
  `fitinput_background_correction` tinyint(1) DEFAULT NULL COMMENT 'is background correction on fit performed?',
  `t_inserted__timestamp` datetime(6) NOT NULL COMMENT 'timestamp of insertion of the data',
  `file_path_plot_sfc_icpms_peakfit` varchar(254) NOT NULL COMMENT 'path to the plot displaying raw data and the fit',
  PRIMARY KEY (`id_exp_icpms`,`name_isotope_analyte`,`name_isotope_internalstandard`,`id_exp_ec_dataset`,`id_fit`),
  KEY `FK_exp_icpms_sfc_fitting_id_exp_ec_dataset_idx` (`id_exp_ec_dataset`),
  CONSTRAINT `FK_exp_icpms_sfc_fitting_id_exp_ec_dataset` FOREIGN KEY (`id_exp_ec_dataset`) REFERENCES `exp_ec_datasets` (`id_exp_ec_dataset`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `FK_exp_icpms_sfc_fitting_id_exp_icpms_name_isotope` FOREIGN KEY (`id_exp_icpms`, `name_isotope_analyte`, `name_isotope_internalstandard`) REFERENCES `exp_icpms_analyte_internalstandard` (`id_exp_icpms`, `name_isotope_analyte`, `name_isotope_internalstandard`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Stores results from sfc icpms fits as performed by Fit_SFC_ICP_MS_Dissolution.py';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ana_icpms_sfc_fitting_peaks`
--

DROP TABLE IF EXISTS `ana_icpms_sfc_fitting_peaks`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ana_icpms_sfc_fitting_peaks` (
  `id_exp_icpms` int NOT NULL COMMENT 'index of icpms experiment',
  `name_isotope_analyte` varchar(45) NOT NULL COMMENT 'name of the analyte used as internalstandard',
  `name_isotope_internalstandard` varchar(45) NOT NULL COMMENT 'name of the isotope used as internalstandard',
  `id_exp_ec_dataset` int NOT NULL COMMENT 'dataset of ec experiments, can be one or multiple id_exp_sfc as defined by exp_ec_datasets_definer',
  `id_fit` int NOT NULL COMMENT 'index of the processed fit. Default = 0, higher if multiple fits have been performed on the same data.',
  `id_peak` int NOT NULL COMMENT 'id of the peak',
  `fit_type` varchar(45) NOT NULL COMMENT 'for each peak the fit parameter for single and sum are stored.\nsingle: fit of the peak just considering amounts of datapoints around the peak (exp_icpms_sfc_fitting.fitinput_datapoints_fit_single_peak or less if another peak is close)\nsum: fit parameters of the single peak (mode) within the fit of all peaks.',
  `area__ng_cm2` double NOT NULL COMMENT 'fit parameter: area of the fitted peak',
  `area_error__ng_cm2` float NOT NULL COMMENT 'error of fit parameter: area of the fitted peak',
  `ln_std` float NOT NULL COMMENT 'fit parameter: natural logarithm',
  `ln_std_error` float NOT NULL COMMENT 'error of fit parameter: natural logarithm',
  `xc__s` double NOT NULL COMMENT 'fit parameter: mean of the lognormal distribution',
  `xc_error__s` float NOT NULL COMMENT 'error of fit parameter: mean of the lognormal distribution',
  `mode__s` float NOT NULL COMMENT 'time of the icpms peak',
  `mode_error__s` float NOT NULL COMMENT 'error in the time of icpms peak',
  `mode_potential__VvsRHE` float DEFAULT NULL COMMENT 'correlated potential of the icpms peak',
  `mode_potential_error__VvsRHE` float DEFAULT NULL COMMENT 'error of the correlated potential, derived by error in time from fitting routine. Error in delay time (t_delay__s) of exp_icpms_sfc not considered!',
  `R2adj` float DEFAULT NULL COMMENT 'Goodness of single fit. Only applies for fit_type =''single''',
  `peak_initial_id_data_icpms` float DEFAULT NULL COMMENT 'id_data_icpms of initially chosen peak in icpms signal',
  `peak_selection` enum('auto','manual') DEFAULT NULL COMMENT 'peak is selected by auto algorithm or manually',
  `peak_manual_time__s` float DEFAULT NULL COMMENT 'manually set position of peak in time axis synchronized between ec and icpms. Only applies if peak_selection = ''manual''',
  PRIMARY KEY (`id_exp_icpms`,`name_isotope_analyte`,`name_isotope_internalstandard`,`id_exp_ec_dataset`,`id_fit`,`id_peak`,`fit_type`),
  KEY `FK_exp_icpms_sfc_fitting_peaks_id_fitting_idx` (`id_exp_icpms`,`name_isotope_analyte`,`name_isotope_internalstandard`,`id_exp_ec_dataset`),
  CONSTRAINT `FK_exp_icpms_sfc_fitting_peaks_id_fitting` FOREIGN KEY (`id_exp_icpms`, `name_isotope_analyte`, `name_isotope_internalstandard`, `id_exp_ec_dataset`, `id_fit`) REFERENCES `ana_icpms_sfc_fitting` (`id_exp_icpms`, `name_isotope_analyte`, `name_isotope_internalstandard`, `id_exp_ec_dataset`, `id_fit`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Stores details of peaks for fits in exp_icpms_sfc_peaks';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ana_integrations`
--

DROP TABLE IF EXISTS `ana_integrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ana_integrations` (
  `id_ana_integration` int NOT NULL AUTO_INCREMENT COMMENT 'index of the integration analysis',
  `id_data_integration_baseline` int NOT NULL COMMENT 'index of the data of the corresponding experiment (ICPMS) or dataset (EC) for the chosen baseline point',
  `id_data_integration_begin` int NOT NULL COMMENT 'index of the data of the corresponding experiment (ICPMS) or dataset (EC) for the bgeinning of integration',
  `id_data_integration_end` int NOT NULL COMMENT 'index of the data of the corresponding experiment (ICPMS) or dataset (EC) for the end of integration',
  `t_integration_baseline__timestamp` datetime(6) NOT NULL COMMENT 'timestamp of chosen baseline point (redundant information, but difficult to query timestamp for ec_datasets from id_data_integration...)',
  `t_integration_begin__timestamp` datetime(6) NOT NULL COMMENT 'timestamp of beginning of integration (redundant information, but difficult to query timestamp for ec_datasets from id_data_integration...)',
  `t_integration_end__timestamp` datetime(6) NOT NULL COMMENT 'timestamp of end of integration (redundant information, but difficult to query timestamp for ec_datasets from id_data_integration...)',
  `area_integrated_simps` float NOT NULL COMMENT 'integrated area following Simpson''''s rule using python module scipy ',
  `area_integrated_trapz` float NOT NULL COMMENT 'trapezoidal integrated area using python module numpy.trapz',
  `y_offset` float DEFAULT NULL COMMENT 'y offset between begin and end of integration',
  `no_of_datapoints_avg` int NOT NULL COMMENT 'number of datapoints used to average baseline and end value and calculate the y offset',
  `no_of_datapoints_rolling` int NOT NULL COMMENT 'number of datapoints to smoothen the curve, used as parameter for auto finding integration points',
  `auto_integration` tinyint(1) NOT NULL COMMENT 'integration points found by algorithm or manually changed by user',
  PRIMARY KEY (`id_ana_integration`)
) ENGINE=InnoDB AUTO_INCREMENT=707 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='stores all integration data';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `counter_electrodes`
--

DROP TABLE IF EXISTS `counter_electrodes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `counter_electrodes` (
  `name_CE` varchar(40) NOT NULL COMMENT 'user given name of th ecounter electrode. It has to be unique!',
  `material` varchar(40) NOT NULL COMMENT 'Material of the CE',
  `manufacturer` varchar(45) NOT NULL COMMENT 'Manufacturing company of the CE',
  `model` varchar(45) NOT NULL COMMENT 'Model name of the CE given by the company or specifications needed for ordering the electrode (to be able to reorder)',
  PRIMARY KEY (`name_CE`),
  UNIQUE KEY `name` (`name_CE`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Inventory list of avaiable counter electrode types. Different CEs of the same type are treated as one entry.';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `data_compression`
--

DROP TABLE IF EXISTS `data_compression`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `data_compression` (
  `id_exp_sfc` int NOT NULL COMMENT 'index for each comprssion experiment connection to exp_sfc',
  `id_data_compression` int NOT NULL COMMENT 'index for the specific data point in a experiment used for the database internally. ',
  `Timestamp` varchar(45) NOT NULL COMMENT 'timestamp of the datapoint',
  `t__s` float NOT NULL COMMENT 'time in seconds since start of the experiment',
  `z_pos__mm` float NOT NULL COMMENT 'position of the z linear axis',
  `force__N` float NOT NULL COMMENT 'measured force',
  PRIMARY KEY (`id_exp_sfc`,`id_data_compression`),
  CONSTRAINT `FK_data_compression` FOREIGN KEY (`id_exp_sfc`) REFERENCES `exp_compression` (`id_exp_sfc`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Contains compression data measured in compression experiments';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `data_ec`
--

DROP TABLE IF EXISTS `data_ec`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `data_ec` (
  `id_exp_sfc` int NOT NULL COMMENT 'connects experimental data (data_ec) to experiment parameters (exp_ec)',
  `id_data_ec` int NOT NULL COMMENT 'index for the specific data point in a experiment used for the database internally. ',
  `Timestamp` varchar(45) DEFAULT NULL COMMENT 'timestamp of the datapoint',
  `t__s` float NOT NULL COMMENT 'time in seconds since start of the experiment',
  `E_WE_raw__VvsRE` float NOT NULL COMMENT 'working electrode potential against the reference electrode potential, insitu iR drop corrected if R_u__ohm is given.',
  `Delta_E_WE_uncomp__V` float NOT NULL COMMENT 'difference of working electrode potential due to the insitu iR-drop compensation. Similar values can be derived by E_WE_raw__VvsRE*R_u__ohm*iR_corr_in_situ__percent/100',
  `E_Signal__VvsRE` float NOT NULL COMMENT 'potential value with which the potentiostat started the internal feedback loop for that measurement point (or something like this). Not important for normal usage. For further information study working principle of a potentiostat or consult gamry documentation.',
  `I__A` float NOT NULL COMMENT 'current flowing between working and counter electrode during that measurement point. Given in Amperes.',
  `overload` int NOT NULL COMMENT 'Overload error report from the potentiostat. Convert the given number to binary system, each 0 reflects an error occured during the measuerment. Possible errors: ''I History'': 1,  ''I OVLD'': 2,  ''CA History'': 4, ''CA OVLD'': 8, ''V OVLD'': 16, ''Overrun'': 32,''''Heatsink'': 64, ''Powersupply'': 128, ''H settling'': 256,  ''S settling'': 512,  ''I ADC railed'': 1024,  ''V ADC railed'': 2048,  ''A ADC railed'': 4096. There is an in-built function in the SFC Software to determine whether and which error occured during a measurment.',
  `cycle` int NOT NULL COMMENT 'Number of cycle for cyclic methods',
  PRIMARY KEY (`id_exp_sfc`,`id_data_ec`),
  CONSTRAINT `FK_exp_ec_data_ec` FOREIGN KEY (`id_exp_sfc`) REFERENCES `exp_ec` (`id_exp_sfc`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Data table of all electrochemal direct current experiments identified by id_exp_ec';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Temporary view structure for view `data_ec_analysis`
--

DROP TABLE IF EXISTS `data_ec_analysis`;
/*!50001 DROP VIEW IF EXISTS `data_ec_analysis`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `data_ec_analysis` AS SELECT 
 1 AS `id_exp_sfc`,
 1 AS `id_data_ec`,
 1 AS `t__s`,
 1 AS `Timestamp`,
 1 AS `E_WE_raw__VvsRE`,
 1 AS `Delta_E_WE_uncomp__V`,
 1 AS `E_Signal__VvsRE`,
 1 AS `I__A`,
 1 AS `overload`,
 1 AS `cycle`,
 1 AS `E_WE__VvsRHE`,
 1 AS `E_WE_uncompensated__VvsRHE`,
 1 AS `E_WE_raw__VvsRHE`,
 1 AS `j__mA_cm2geo_spot_size`,
 1 AS `j__mA_cm2geo_fc_top_cell_Aideal`,
 1 AS `j__mA_cm2geo_fc_top_cell_Areal`,
 1 AS `j__mA_cm2geo_fc_top_sealing`,
 1 AS `j__mA_cm2geo_fc_top_PTL`,
 1 AS `j__mA_cm2geo_fc_bottom_cell_Aideal`,
 1 AS `j__mA_cm2geo_fc_bottom_cell_Areal`,
 1 AS `j__mA_cm2geo_fc_bottom_sealing`,
 1 AS `j__mA_cm2geo_fc_bottom_PTL`*/;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `data_ec_polcurve`
--

DROP TABLE IF EXISTS `data_ec_polcurve`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `data_ec_polcurve` (
  `id_exp_ec_polcurve` int NOT NULL COMMENT 'index of polcurve',
  `id_data_ec_polcurve` int NOT NULL COMMENT 'dataindex within one polcurve',
  `id_exp_sfc_ghold` int NOT NULL COMMENT 'index of sfc experiment of the ghold',
  `id_exp_sfc_geis` int NOT NULL COMMENT 'index of sfc experiment of the geis',
  `id_current_step` int NOT NULL COMMENT 'index of the current step, same current density of forward and backward scan get same index and can be differentiated by scan_direction',
  `scan_direction` int NOT NULL COMMENT 'does it belong to forward (1) or backward (2) scan',
  `id_data_eis_chosen_Ru` int NOT NULL COMMENT 'id_data_eis from the datapoint used for the uncompensated resistance value',
  `R_u_derived_by` enum('manual','minimum','intercept') DEFAULT NULL COMMENT '''manual'' chosen by manual user interaction\\n ''minimum'': chosen as the minimum value of minusZ_img__ohm\\n ''intercept'': chsoen as the x-axis intercept when going from high to low frequencies',
  `overload_list` varchar(254) NOT NULL COMMENT 'list of overload error message received during the ghold measurement',
  `gooddata` tinyint DEFAULT NULL COMMENT 'user chosen bool wether or not datapoint is consideres as good',
  `I__A` float NOT NULL COMMENT 'averaged absolute current in the slected segement of ghold. Number of datapoints of the ghold used is defined in exp_ec_polcurve - number_datapoints_in_tail',
  `I__A_std` float NOT NULL COMMENT 'standard deviation of the current in the slected segement of ghold',
  `I_drift__A_s` float NOT NULL COMMENT 'drift of current over time in selected segment',
  `E_WE_uncompensated__VvsRHE` float NOT NULL COMMENT 'averaged potential in the slected segement of ghold. Number of datapoints of the ghold used is defined in exp_ec_polcurve - number_datapoints_in_tail',
  `E_WE_uncompensated__VvsRHE_std` float NOT NULL COMMENT 'standard deviation of the potential in the slected segement of ghold',
  `E_WE_uncompensated_drift__V_s` float NOT NULL COMMENT 'drift of potential over time in selected segment',
  PRIMARY KEY (`id_exp_ec_polcurve`,`id_data_ec_polcurve`),
  UNIQUE KEY `id_exp_sfc_ghold_UNIQUE` (`id_exp_sfc_ghold`) /*!80000 INVISIBLE */,
  UNIQUE KEY `id_exp_sfc_geis_UNIQUE` (`id_exp_sfc_geis`),
  CONSTRAINT `FK_data_ec_polcurve_id_exp_ec_polcurve` FOREIGN KEY (`id_exp_ec_polcurve`) REFERENCES `exp_ec_polcurve` (`id_exp_ec_polcurve`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `FK_data_ec_polcurve_id_exp_sfc_geis` FOREIGN KEY (`id_exp_sfc_geis`) REFERENCES `exp_ec_geis` (`id_exp_sfc`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `FK_data_ec_polcurve_id_exp_sfc_ghold` FOREIGN KEY (`id_exp_sfc_ghold`) REFERENCES `exp_ec_ghold` (`id_exp_sfc`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='averaged data of polarization curve experiments';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Temporary view structure for view `data_ec_polcurve_analysis`
--

DROP TABLE IF EXISTS `data_ec_polcurve_analysis`;
/*!50001 DROP VIEW IF EXISTS `data_ec_polcurve_analysis`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `data_ec_polcurve_analysis` AS SELECT 
 1 AS `id_exp_ec_polcurve`,
 1 AS `id_data_ec_polcurve`,
 1 AS `id_exp_sfc_ghold`,
 1 AS `id_exp_sfc_geis`,
 1 AS `id_current_step`,
 1 AS `scan_direction`,
 1 AS `id_data_eis_chosen_Ru`,
 1 AS `R_u__ohm`,
 1 AS `overload_list`,
 1 AS `gooddata`,
 1 AS `I__A`,
 1 AS `I__A_std`,
 1 AS `I_drift__A_s`,
 1 AS `E_WE_uncompensated__VvsRHE`,
 1 AS `E_WE_uncompensated__VvsRHE_std`,
 1 AS `E_WE_uncompensated_drift__V_s`,
 1 AS `E_WE__VvsRHE`,
 1 AS `j__mA_cm2geo_spot_size`,
 1 AS `j__mA_cm2geo_fc_top_cell_Aideal`,
 1 AS `j__mA_cm2geo_fc_top_cell_Areal`,
 1 AS `j__mA_cm2geo_fc_top_sealing`,
 1 AS `j__mA_cm2geo_fc_top_PTL`,
 1 AS `j__mA_cm2geo_fc_bottom_cell_Aideal`,
 1 AS `j__mA_cm2geo_fc_bottom_cell_Areal`,
 1 AS `j__mA_cm2geo_fc_bottom_sealing`,
 1 AS `j__mA_cm2geo_fc_bottom_PTL`,
 1 AS `I_hold__A`,
 1 AS `t_hold__s`,
 1 AS `t_samplerate__s`,
 1 AS `f_initial__Hz`,
 1 AS `f_final__Hz`,
 1 AS `I_dc__A`,
 1 AS `I_amplitude__A`,
 1 AS `R_initialguess__ohm`,
 1 AS `points_per_decade`*/;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `data_eis`
--

DROP TABLE IF EXISTS `data_eis`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `data_eis` (
  `id_exp_sfc` int NOT NULL COMMENT 'connects experimental data (data_eis) to experiment parameters (exp_ec)',
  `id_data_eis` int NOT NULL COMMENT 'index for the specific data point in a experiment used for the database internally. ',
  `Timestamp` varchar(45) DEFAULT NULL COMMENT 'Timestamp of the end of the eis frequency measurement. Not given by Gamry potentiostat but clauclated by Labview software',
  `t__s` float DEFAULT NULL COMMENT 'time in seconds since start of the experiment. Is not available for gamry potentiostats, it could only be calculated by SFC software during the measurement which might be inaccurate.',
  `f__Hz` float NOT NULL COMMENT 'frequency of the impedance measurement in Hertz',
  `Z_real__ohm` float NOT NULL COMMENT 'real part of the impedanze in Ohm',
  `minusZ_img__ohm` float NOT NULL COMMENT 'negative imaginary part of the impedance in Ohm',
  `E_dc__VvsRE` float DEFAULT NULL COMMENT 'dc value of the working electrode potential during the eis measurment',
  `I_dc__A` float DEFAULT NULL COMMENT 'dc value of the current between working and counter electrode during the eis measurment',
  PRIMARY KEY (`id_exp_sfc`,`id_data_eis`),
  CONSTRAINT `FK_exp_ec_data_impedance` FOREIGN KEY (`id_exp_sfc`) REFERENCES `exp_ec` (`id_exp_sfc`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Data table of all electrochemical impedance spectroscopy experiments identified by id_exp_ec';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Temporary view structure for view `data_eis_analysis`
--

DROP TABLE IF EXISTS `data_eis_analysis`;
/*!50001 DROP VIEW IF EXISTS `data_eis_analysis`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `data_eis_analysis` AS SELECT 
 1 AS `id_exp_sfc`,
 1 AS `id_data_eis`,
 1 AS `t__s`,
 1 AS `Timestamp`,
 1 AS `f__Hz`,
 1 AS `Z_real__ohm`,
 1 AS `minusZ_img__ohm`,
 1 AS `E_dc__VvsRE`,
 1 AS `I_dc__A`,
 1 AS `E_WE_uncompensated__VvsRHE`,
 1 AS `j__mA_cm2geo_spot_size`,
 1 AS `j__mA_cm2geo_fc_top_cell_Aideal`,
 1 AS `j__mA_cm2geo_fc_top_cell_Areal`,
 1 AS `j__mA_cm2geo_fc_top_sealing`,
 1 AS `j__mA_cm2geo_fc_top_PTL`,
 1 AS `j__mA_cm2geo_fc_bottom_cell_Aideal`,
 1 AS `j__mA_cm2geo_fc_bottom_cell_Areal`,
 1 AS `j__mA_cm2geo_fc_bottom_sealing`,
 1 AS `j__mA_cm2geo_fc_bottom_PTL`*/;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `data_icpms`
--

DROP TABLE IF EXISTS `data_icpms`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `data_icpms` (
  `id_exp_icpms` int NOT NULL COMMENT 'Index of the icpms experiment.',
  `name_isotope_analyte` varchar(45) NOT NULL COMMENT 'name of the analyte isotope',
  `name_isotope_internalstandard` varchar(45) NOT NULL COMMENT 'name of the corresponding internal standard isotope',
  `id_data_icpms` int NOT NULL COMMENT 'index for the specific data point in am icpms experiment used for the database internally. ',
  `t__s` float NOT NULL COMMENT 'time in seconds since start of the experiment',
  `counts_analyte` float NOT NULL COMMENT 'counts of the analyt isotope',
  `counts_internalstandard` float NOT NULL COMMENT 'counts of the internal standard',
  PRIMARY KEY (`id_exp_icpms`,`name_isotope_analyte`,`name_isotope_internalstandard`,`id_data_icpms`),
  KEY `FK_data_icpms_id_exp_icpms_analyte_idx` (`id_exp_icpms`,`name_isotope_analyte`,`name_isotope_internalstandard`),
  CONSTRAINT `FK_data_icpms_id_exp_icpms_analyte` FOREIGN KEY (`id_exp_icpms`, `name_isotope_analyte`, `name_isotope_internalstandard`) REFERENCES `exp_icpms_analyte_internalstandard` (`id_exp_icpms`, `name_isotope_analyte`, `name_isotope_internalstandard`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Data for all icp_ms experiments. Table stores one analyte-internal standard relationship per time step. If multiple analyte-internalstandard relations are measured they will produce multiple rows.';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `data_icpms_internalstandard_fitting`
--

DROP TABLE IF EXISTS `data_icpms_internalstandard_fitting`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `data_icpms_internalstandard_fitting` (
  `id_exp_icpms` int NOT NULL COMMENT 'Index of the icpms experiment.',
  `name_isotope_analyte` varchar(45) NOT NULL COMMENT 'name of the analyte isotope',
  `name_isotope_internalstandard` varchar(45) NOT NULL COMMENT 'name of the corresponding internal standard isotope',
  `id_data_icpms` int NOT NULL COMMENT 'index for the specific data point in am icpms experiment used for the database internally. ',
  `counts_internalstandard_fitted` float DEFAULT NULL COMMENT 'Internalstandard counts fitted by linear fit experimentwise. An experiment is defined by id_ML or combination of multiple id_MLs performed so close to each other that they overlap considering t_srtart_shift and t_end_shift.',
  PRIMARY KEY (`id_exp_icpms`,`name_isotope_analyte`,`name_isotope_internalstandard`,`id_data_icpms`),
  KEY `FK_data_icpms_id_exp_icpms_analyte_idx` (`id_exp_icpms`,`name_isotope_analyte`,`name_isotope_internalstandard`),
  KEY `FK_data_icpms_istd_fitting_id_exp_icpms_analyte_idx` (`id_exp_icpms`,`name_isotope_analyte`,`name_isotope_internalstandard`,`id_data_icpms`),
  CONSTRAINT `FK_data_icpms_istd_fitting_id_exp_icpms_analyte` FOREIGN KEY (`id_exp_icpms`, `name_isotope_analyte`, `name_isotope_internalstandard`, `id_data_icpms`) REFERENCES `data_icpms` (`id_exp_icpms`, `name_isotope_analyte`, `name_isotope_internalstandard`, `id_data_icpms`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Data for all icp_ms experiments. Table stores one analyte-internal standard relationship per time step. If multiple analyte-internalstandard relations are measured they will produce multiple rows.';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Temporary view structure for view `data_icpms_sfc_analysis`
--

DROP TABLE IF EXISTS `data_icpms_sfc_analysis`;
/*!50001 DROP VIEW IF EXISTS `data_icpms_sfc_analysis`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `data_icpms_sfc_analysis` AS SELECT 
 1 AS `id_exp_icpms`,
 1 AS `name_isotope_analyte`,
 1 AS `name_isotope_internalstandard`,
 1 AS `id_data_icpms`,
 1 AS `t__s`,
 1 AS `counts_analyte`,
 1 AS `counts_internalstandard`,
 1 AS `counts_internalstandard_fitted`,
 1 AS `name_setup_sfc`,
 1 AS `t__timestamp_sfc_pc`,
 1 AS `t_delaycorrected__timestamp_sfc_pc`,
 1 AS `a_is__countratio`,
 1 AS `c_a__mug_L`,
 1 AS `dm_dt__ng_s`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `data_icpms_sfc_analysis_no_istd_fitting`
--

DROP TABLE IF EXISTS `data_icpms_sfc_analysis_no_istd_fitting`;
/*!50001 DROP VIEW IF EXISTS `data_icpms_sfc_analysis_no_istd_fitting`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `data_icpms_sfc_analysis_no_istd_fitting` AS SELECT 
 1 AS `id_exp_icpms`,
 1 AS `name_isotope_analyte`,
 1 AS `name_isotope_internalstandard`,
 1 AS `id_data_icpms`,
 1 AS `t__s`,
 1 AS `counts_analyte`,
 1 AS `counts_internalstandard`,
 1 AS `counts_internalstandard_fitted`,
 1 AS `name_setup_sfc`,
 1 AS `t__timestamp_sfc_pc`,
 1 AS `t_delaycorrected__timestamp_sfc_pc`,
 1 AS `a_is__countratio`,
 1 AS `c_a__mug_L`,
 1 AS `dm_dt__ng_s`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `data_icpms_sfc_analysis_old`
--

DROP TABLE IF EXISTS `data_icpms_sfc_analysis_old`;
/*!50001 DROP VIEW IF EXISTS `data_icpms_sfc_analysis_old`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `data_icpms_sfc_analysis_old` AS SELECT 
 1 AS `id_exp_icpms`,
 1 AS `name_isotope_analyte`,
 1 AS `name_isotope_internalstandard`,
 1 AS `id_data_icpms`,
 1 AS `t__s`,
 1 AS `counts_analyte`,
 1 AS `counts_internalstandard`,
 1 AS `name_setup_sfc`,
 1 AS `t__timestamp_sfc_pc`,
 1 AS `t_delaycorrected__timestamp_sfc_pc`,
 1 AS `a_is__countratio`,
 1 AS `c_a__mug_L`,
 1 AS `dm_dt__ng_s`,
 1 AS `id_exp_sfc`,
 1 AS `dm_dt_S__ng_s_cm2geo_spot_size`,
 1 AS `dm_dt_S__ng_s_cm2geo_fc_top_cell_Aideal`,
 1 AS `dm_dt_S__ng_s_cm2geo_fc_top_cell_Areal`,
 1 AS `dm_dt_S__ng_s_cm2geo_fc_top_sealing`,
 1 AS `dm_dt_S__ng_s_cm2geo_fc_top_PTL`,
 1 AS `dm_dt_S__ng_s_cm2geo_fc_bottom_cell_Aideal`,
 1 AS `dm_dt_S__ng_s_cm2geo_fc_bottom_cell_Areal`,
 1 AS `dm_dt_S__ng_s_cm2geo_fc_bottom_sealing`,
 1 AS `dm_dt_S__ng_s_cm2geo_fc_bottom_PTL`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `data_icpms_sfc_batch_analysis`
--

DROP TABLE IF EXISTS `data_icpms_sfc_batch_analysis`;
/*!50001 DROP VIEW IF EXISTS `data_icpms_sfc_batch_analysis`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `data_icpms_sfc_batch_analysis` AS SELECT 
 1 AS `id_exp_icpms`,
 1 AS `name_isotope_analyte`,
 1 AS `name_isotope_internalstandard`,
 1 AS `id_data_icpms`,
 1 AS `t_delaycorrected__timestamp_sfc_pc`,
 1 AS `a_is__countratio`,
 1 AS `c_a__mug_L`,
 1 AS `dm_dt__ng_s`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `data_stability_analysis`
--

DROP TABLE IF EXISTS `data_stability_analysis`;
/*!50001 DROP VIEW IF EXISTS `data_stability_analysis`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `data_stability_analysis` AS SELECT 
 1 AS `name_analysis`,
 1 AS `id_exp_ec_dataset`,
 1 AS `name_exp_ec_dataset`,
 1 AS `name_user`,
 1 AS `comment_icpms`,
 1 AS `comment_ec`,
 1 AS `name_setup_sfc`,
 1 AS `element`,
 1 AS `id_exp_icpms`,
 1 AS `name_isotope_analyte`,
 1 AS `name_isotope_internalstandard`,
 1 AS `id_ana_integration_icpms`,
 1 AS `id_data_integration_icpms_baseline`,
 1 AS `id_data_integration_icpms_begin`,
 1 AS `id_data_integration_icpms_end`,
 1 AS `t_integration_icpms_baseline__timestamp`,
 1 AS `t_integration_icpms_begin__timestamp`,
 1 AS `t_integration_icpms_end__timestamp`,
 1 AS `m_dissolved_simps__ng`,
 1 AS `m_dissolved_trapz__ng`,
 1 AS `dm_dt_offset__ng_s`,
 1 AS `no_of_datapoints_av_icpms`,
 1 AS `no_of_datapoints_rolling_icpms`,
 1 AS `auto_integration_icpms`,
 1 AS `name_sample`,
 1 AS `name_setup_icpms`,
 1 AS `t_start__timestamp_icpms_pc`,
 1 AS `t_duration__s`,
 1 AS `t_duration_planned__s`,
 1 AS `type_experiment`,
 1 AS `plasma_mode`,
 1 AS `tune_mode`,
 1 AS `num_of_scans`,
 1 AS `id_exp_icpms_calibration_set`,
 1 AS `gas_dilution_factor`,
 1 AS `name_gas_collision`,
 1 AS `flow_rate_collision__mL_min`,
 1 AS `name_gas_reaction`,
 1 AS `flow_rate_reaction__mL_min`,
 1 AS `name_computer_inserted_data`,
 1 AS `file_path_rawdata`,
 1 AS `t_inserted_data__timestamp`,
 1 AS `file_name_rawdata`,
 1 AS `t_start_delaycorrected__timestamp_sfc_pc`,
 1 AS `t_end_delaycorrected__timestamp_sfc_pc`,
 1 AS `t_start__timestamp_sfc_pc`,
 1 AS `t_delay__s`,
 1 AS `flow_rate_real__mul_min`,
 1 AS `calibration_slope__countratio_mug_L`,
 1 AS `delta_calibration_slope__countratio_mug_L`,
 1 AS `calibration_intercept__countratio`,
 1 AS `delta_calibration_intercept__countratio`,
 1 AS `Rsquared`,
 1 AS `calibration_method`,
 1 AS `file_path_calibration_plot`,
 1 AS `name_computer_inserted_calibration_data`,
 1 AS `t_inserted_calibration_data__timestamp`,
 1 AS `name_isotope`,
 1 AS `M__g_mol`,
 1 AS `n_dissolved_simps__mol`,
 1 AS `n_dissolved_trapz__mol`,
 1 AS `id_ana_integration_ec`,
 1 AS `name_reaction`,
 1 AS `faradaic_efficiency__percent`,
 1 AS `name_product_of_interest`,
 1 AS `number_electrons`,
 1 AS `id_data_integration_ec_baseline`,
 1 AS `id_data_integration_ec_begin`,
 1 AS `id_data_integration_ec_end`,
 1 AS `t_integration_ec_baseline__timestamp`,
 1 AS `t_integration_ec_begin__timestamp`,
 1 AS `t_integration_ec_end__timestamp`,
 1 AS `Q_integrated_simps__C`,
 1 AS `Q_integrated_trapz__C`,
 1 AS `I_offset__A`,
 1 AS `no_of_datapoints_av_ec`,
 1 AS `no_of_datapoints_rolling_ec`,
 1 AS `auto_integration_ec`,
 1 AS `id_exp_sfc_first`,
 1 AS `id_exp_sfc`,
 1 AS `name_setup_sfc_alias`,
 1 AS `name_setup_sfc_feature`,
 1 AS `name_setup_sfc_type`,
 1 AS `t_start__timestamp`,
 1 AS `t_end__timestamp`,
 1 AS `rawdata_path`,
 1 AS `rawdata_computer`,
 1 AS `id_ML`,
 1 AS `id_ML_technique`,
 1 AS `id_sample`,
 1 AS `id_spot`,
 1 AS `force__N`,
 1 AS `T_stage__degC`,
 1 AS `interrupted`,
 1 AS `labview_sfc_version`,
 1 AS `db_version`,
 1 AS `ec_name_technique`,
 1 AS `ec_R_u__ohm`,
 1 AS `ec_iR_corr_in_situ__percent`,
 1 AS `ec_R_u_determining_exp_ec`,
 1 AS `ec_E_RE__VvsRHE`,
 1 AS `ec_name_RE`,
 1 AS `ec_name_RE_material`,
 1 AS `ec_name_RE_manufacturer`,
 1 AS `ec_name_RE_model`,
 1 AS `ec_name_CE`,
 1 AS `ec_name_CE_material`,
 1 AS `ec_name_CE_manufacturer`,
 1 AS `ec_name_CE_model`,
 1 AS `ec_name_device`,
 1 AS `ec_id_control_mode`,
 1 AS `ec_id_ie_range`,
 1 AS `ec_id_vch_range`,
 1 AS `ec_id_ich_range`,
 1 AS `ec_id_vch_filter`,
 1 AS `ec_id_ich_filter`,
 1 AS `ec_id_ca_speed`,
 1 AS `ec_id_ie_stability`,
 1 AS `ec_id_sampling_mode`,
 1 AS `ec_ie_range_auto`,
 1 AS `ec_vch_range_auto`,
 1 AS `ec_ich_range_auto`,
 1 AS `samples_id_sample`,
 1 AS `samples_name_sample`,
 1 AS `samples_name_user`,
 1 AS `samples_t_manufactured__timestamp`,
 1 AS `samples_comment`,
 1 AS `samples_total_loading__mg_cm2`,
 1 AS `spots_id_spot`,
 1 AS `spots_spot_size__mm2`,
 1 AS `spots_pos_x__mm`,
 1 AS `spots_pos_y__mm`,
 1 AS `spots_comment`,
 1 AS `spots_total_loading__mg_cm2`,
 1 AS `cv_E_initial__VvsRE`,
 1 AS `cv_E_apex1__VvsRE`,
 1 AS `cv_E_apex2__VvsRE`,
 1 AS `cv_E_final__VvsRE`,
 1 AS `cv_scanrate__mV_s`,
 1 AS `cv_stepsize__mV`,
 1 AS `cv_cycles`,
 1 AS `geis_f_initial__Hz`,
 1 AS `geis_f_final__Hz`,
 1 AS `geis_I_dc__A`,
 1 AS `geis_I_amplitude__A`,
 1 AS `geis_R_initialguess__ohm`,
 1 AS `geis_points_per_decade`,
 1 AS `ghold_I_hold__A`,
 1 AS `ghold_t_hold__s`,
 1 AS `ghold_t_samplerate__s`,
 1 AS `peis_f_initial__Hz`,
 1 AS `peis_f_final__Hz`,
 1 AS `peis_E_dc__VvsRE`,
 1 AS `peis_E_amplitude__VvsRE`,
 1 AS `peis_R_initialguess__ohm`,
 1 AS `peis_points_per_decade`,
 1 AS `phold_E_hold__VvsRE`,
 1 AS `phold_t_hold__s`,
 1 AS `phold_t_samplerate__s`,
 1 AS `ppulse_E_hold1__VvsRE`,
 1 AS `ppulse_E_hold2__VvsRE`,
 1 AS `ppulse_t_hold1__s`,
 1 AS `ppulse_t_hold2__s`,
 1 AS `ppulse_t_samplerate__s`,
 1 AS `ppulse_cycles`,
 1 AS `gpulse_I_hold1__A`,
 1 AS `gpulse_I_hold2__A`,
 1 AS `gpulse_t_hold1__s`,
 1 AS `gpulse_t_hold2__s`,
 1 AS `gpulse_t_samplerate__s`,
 1 AS `gpulse_cycles`,
 1 AS `ramp_E_initial__VvsRE`,
 1 AS `ramp_E_final__VvsRE`,
 1 AS `ramp_scanrate__mV_s`,
 1 AS `ramp_stepsize__mV`,
 1 AS `ramp_cycles`,
 1 AS `fc_top_name_flow_cell`,
 1 AS `fc_top_name_flow_cell_name_user`,
 1 AS `fc_top_name_flow_cell_material`,
 1 AS `fc_top_name_flow_cell_A_opening_ideal__mm2`,
 1 AS `fc_top_name_flow_cell_A_opening_real__mm2`,
 1 AS `fc_top_name_flow_cell_manufacture_date`,
 1 AS `fc_top_name_flow_cell_CAD_file`,
 1 AS `fc_top_name_flow_cell_comment`,
 1 AS `fc_top_id_sealing`,
 1 AS `fc_top_id_sealing_name_user`,
 1 AS `fc_top_id_sealing_material`,
 1 AS `fc_top_id_sealing_A_sealing__mm2`,
 1 AS `fc_top_id_sealing_A_opening__mm2`,
 1 AS `fc_top_id_sealing_thickness__mm`,
 1 AS `fc_top_id_sealing_shaping_method`,
 1 AS `fc_top_id_sealing_comment`,
 1 AS `fc_top_id_PTL`,
 1 AS `fc_top_id_PTL_name_user`,
 1 AS `fc_top_id_PTL_material`,
 1 AS `fc_top_id_PTL_thickness__mm`,
 1 AS `fc_top_id_PTL_manufacturer`,
 1 AS `fc_top_id_PTL_A_PTL__mm2`,
 1 AS `fc_top_id_PTL_shaping_method`,
 1 AS `fc_top_id_PTL_comment`,
 1 AS `fc_bottom_name_flow_cell`,
 1 AS `fc_bottom_name_flow_cell_name_user`,
 1 AS `fc_bottom_name_flow_cell_material`,
 1 AS `fc_bottom_name_flow_cell_A_opening_ideal__mm2`,
 1 AS `fc_bottom_name_flow_cell_A_opening_real__mm2`,
 1 AS `fc_bottom_name_flow_cell_manufacture_date`,
 1 AS `fc_bottom_name_flow_cell_CAD_file`,
 1 AS `fc_bottom_name_flow_cell_comment`,
 1 AS `fc_bottom_id_sealing`,
 1 AS `fc_bottom_id_sealing_name_user`,
 1 AS `fc_bottom_id_sealing_material`,
 1 AS `fc_bottom_id_sealing_A_sealing__mm2`,
 1 AS `fc_bottom_id_sealing_A_opening__mm2`,
 1 AS `fc_bottom_id_sealing_thickness__mm`,
 1 AS `fc_bottom_id_sealing_shaping_method`,
 1 AS `fc_bottom_id_sealing_comment`,
 1 AS `fc_bottom_id_PTL`,
 1 AS `fc_bottom_id_PTL_name_user`,
 1 AS `fc_bottom_id_PTL_material`,
 1 AS `fc_bottom_id_PTL_thickness__mm`,
 1 AS `fc_bottom_id_PTL_manufacturer`,
 1 AS `fc_bottom_id_PTL_A_PTL__mm2`,
 1 AS `fc_bottom_id_PTL_shaping_method`,
 1 AS `fc_bottom_id_PTL_comment`,
 1 AS `fe_top_id_pump_in`,
 1 AS `fe_top_id_pump_in_manufacturer`,
 1 AS `fe_top_id_pump_in_model`,
 1 AS `fe_top_id_pump_in_device`,
 1 AS `fe_top_id_tubing_in`,
 1 AS `fe_top_id_tubing_in_name_tubing`,
 1 AS `fe_top_id_tubing_in_inner_diameter__mm`,
 1 AS `fe_top_id_tubing_in_color_code`,
 1 AS `fe_top_id_tubing_in_manufacturer`,
 1 AS `fe_top_id_tubing_in_model`,
 1 AS `fe_top_pump_rate_in__rpm`,
 1 AS `fe_top_id_pump_out`,
 1 AS `fe_top_id_pump_out_manufacturer`,
 1 AS `fe_top_id_pump_out_model`,
 1 AS `fe_top_id_pump_out_device`,
 1 AS `fe_top_id_tubing_out`,
 1 AS `fe_top_id_tubing_out_name_tubing`,
 1 AS `fe_top_id_tubing_out_inner_diameter__mm`,
 1 AS `fe_top_id_tubing_out_color_code`,
 1 AS `fe_top_id_tubing_out_manufacturer`,
 1 AS `fe_top_id_tubing_out_model`,
 1 AS `fe_top_pump_rate_out__rpm`,
 1 AS `fe_top_flow_rate_real__mul_min`,
 1 AS `fe_top_name_electrolyte`,
 1 AS `fe_top_c_electrolyte__mol_L`,
 1 AS `fe_top_T_electrolyte__degC`,
 1 AS `fe_bottom_id_pump_in`,
 1 AS `fe_bottom_id_pump_in_manufacturer`,
 1 AS `fe_bottom_id_pump_in_model`,
 1 AS `fe_bottom_id_pump_in_device`,
 1 AS `fe_bottom_id_tubing_in`,
 1 AS `fe_bottom_id_tubing_in_name_tubing`,
 1 AS `fe_bottom_id_tubing_in_inner_diameter__mm`,
 1 AS `fe_bottom_id_tubing_in_color_code`,
 1 AS `fe_bottom_id_tubing_in_manufacturer`,
 1 AS `fe_bottom_id_tubing_in_model`,
 1 AS `fe_bottom_pump_rate_in__rpm`,
 1 AS `fe_bottom_id_pump_out`,
 1 AS `fe_bottom_id_pump_out_manufacturer`,
 1 AS `fe_bottom_id_pump_out_model`,
 1 AS `fe_bottom_id_pump_out_device`,
 1 AS `fe_bottom_id_tubing_out`,
 1 AS `fe_bottom_id_tubing_out_name_tubing`,
 1 AS `fe_bottom_id_tubing_out_inner_diameter__mm`,
 1 AS `fe_bottom_id_tubing_out_color_code`,
 1 AS `fe_bottom_id_tubing_out_manufacturer`,
 1 AS `fe_bottom_id_tubing_out_model`,
 1 AS `fe_bottom_pump_rate_out__rpm`,
 1 AS `fe_bottom_flow_rate_real__mul_min`,
 1 AS `fe_bottom_name_electrolyte`,
 1 AS `fe_bottom_c_electrolyte__mol_L`,
 1 AS `fe_bottom_T_electrolyte__degC`,
 1 AS `fg_top_Arring_name_gas`,
 1 AS `fg_top_Arring_flow_rate__mL_min`,
 1 AS `fg_top_purgevial_name_gas`,
 1 AS `fg_top_purgevial_flow_rate__mL_min`,
 1 AS `fg_top_main_name_gas`,
 1 AS `fg_top_main_flow_rate__mL_min`,
 1 AS `fg_bottom_Arring_name_gas`,
 1 AS `fg_bottom_Arring_flow_rate__mL_min`,
 1 AS `fg_bottom_purgevial_name_gas`,
 1 AS `fg_bottom_purgevial_flow_rate__mL_min`,
 1 AS `fg_bottom_main_name_gas`,
 1 AS `fg_bottom_main_flow_rate__mL_min`,
 1 AS `location`,
 1 AS `n_product_of_interest_simps__mol`,
 1 AS `n_product_of_interest_trapz__mol`,
 1 AS `S_number_simps`,
 1 AS `S_number_trapz`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `data_stability_batch_analysis`
--

DROP TABLE IF EXISTS `data_stability_batch_analysis`;
/*!50001 DROP VIEW IF EXISTS `data_stability_batch_analysis`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `data_stability_batch_analysis` AS SELECT 
 1 AS `id_exp_icpms`,
 1 AS `name_isotope_analyte`,
 1 AS `name_isotope_internalstandard`,
 1 AS `name_analysis`,
 1 AS `id_exp_ec_dataset`,
 1 AS `name_exp_ec_dataset`,
 1 AS `id_exp_icpms_sfc_online`,
 1 AS `id_exp_icpms_calibration_set`,
 1 AS `name_setup_sfc`,
 1 AS `location`,
 1 AS `t_delay__s`,
 1 AS `t_start__timestamp_sfc_pc`,
 1 AS `t_end__timestamp_sfc_pc`,
 1 AS `t_start_delaycorrected__timestamp_sfc_pc`,
 1 AS `t_end_delaycorrected__timestamp_sfc_pc`,
 1 AS `m_start__g`,
 1 AS `m_end__g`,
 1 AS `density__g_mL`,
 1 AS `comment`,
 1 AS `name_sample`,
 1 AS `name_user`,
 1 AS `name_setup_icpms`,
 1 AS `t_start__timestamp_icpms_pc`,
 1 AS `t_duration__s`,
 1 AS `t_duration_planned__s`,
 1 AS `type_experiment`,
 1 AS `plasma_mode`,
 1 AS `tune_mode`,
 1 AS `num_of_scans`,
 1 AS `gas_dilution_factor`,
 1 AS `name_gas_collision`,
 1 AS `flow_rate_collision__mL_min`,
 1 AS `name_gas_reaction`,
 1 AS `flow_rate_reaction__mL_min`,
 1 AS `name_computer_inserted_data`,
 1 AS `file_path_rawdata`,
 1 AS `t_inserted_data__timestamp`,
 1 AS `file_name_rawdata`,
 1 AS `c_analyte__mug_L`,
 1 AS `c_internalstandard__mug_L`,
 1 AS `t_integration_analyte__s`,
 1 AS `t_integration_internalstandard__s`,
 1 AS `a_is__countratio`,
 1 AS `a_is_std__countratio`,
 1 AS `calibration_slope__countratio_mug_L`,
 1 AS `delta_calibration_slope__countratio_mug_L`,
 1 AS `calibration_intercept__countratio`,
 1 AS `delta_calibration_intercept__countratio`,
 1 AS `Rsquared`,
 1 AS `calibration_method`,
 1 AS `file_path_calibration_plot`,
 1 AS `name_computer_inserted_calibration_data`,
 1 AS `t_inserted_calibration_data__timestamp`,
 1 AS `Delta_t__s`,
 1 AS `flow_rate_real__mul_min`,
 1 AS `c_a__mug_L`,
 1 AS `dm_dt__ng_s`,
 1 AS `m_batch__ng`,
 1 AS `n_batch__mol`,
 1 AS `id_ana_integration_ec`,
 1 AS `name_reaction`,
 1 AS `faradaic_efficiency__percent`,
 1 AS `name_product_of_interest`,
 1 AS `number_electrons`,
 1 AS `id_data_integration_ec_baseline`,
 1 AS `id_data_integration_ec_begin`,
 1 AS `id_data_integration_ec_end`,
 1 AS `t_integration_ec_baseline__timestamp`,
 1 AS `t_integration_ec_begin__timestamp`,
 1 AS `t_integration_ec_end__timestamp`,
 1 AS `Q_integrated_simps__C`,
 1 AS `Q_integrated_trapz__C`,
 1 AS `I_offset__A`,
 1 AS `no_of_datapoints_av_ec`,
 1 AS `no_of_datapoints_rolling_ec`,
 1 AS `auto_integration_ec`,
 1 AS `id_exp_sfc_first`,
 1 AS `id_exp_sfc`,
 1 AS `name_setup_sfc_alias`,
 1 AS `name_setup_sfc_feature`,
 1 AS `name_setup_sfc_type`,
 1 AS `t_start__timestamp`,
 1 AS `t_end__timestamp`,
 1 AS `rawdata_path`,
 1 AS `rawdata_computer`,
 1 AS `id_ML`,
 1 AS `id_ML_technique`,
 1 AS `id_sample`,
 1 AS `id_spot`,
 1 AS `force__N`,
 1 AS `T_stage__degC`,
 1 AS `interrupted`,
 1 AS `labview_sfc_version`,
 1 AS `db_version`,
 1 AS `ec_name_technique`,
 1 AS `ec_R_u__ohm`,
 1 AS `ec_iR_corr_in_situ__percent`,
 1 AS `ec_R_u_determining_exp_ec`,
 1 AS `ec_E_RE__VvsRHE`,
 1 AS `ec_name_RE`,
 1 AS `ec_name_RE_material`,
 1 AS `ec_name_RE_manufacturer`,
 1 AS `ec_name_RE_model`,
 1 AS `ec_name_CE`,
 1 AS `ec_name_CE_material`,
 1 AS `ec_name_CE_manufacturer`,
 1 AS `ec_name_CE_model`,
 1 AS `ec_name_device`,
 1 AS `ec_id_control_mode`,
 1 AS `ec_id_ie_range`,
 1 AS `ec_id_vch_range`,
 1 AS `ec_id_ich_range`,
 1 AS `ec_id_vch_filter`,
 1 AS `ec_id_ich_filter`,
 1 AS `ec_id_ca_speed`,
 1 AS `ec_id_ie_stability`,
 1 AS `ec_id_sampling_mode`,
 1 AS `ec_ie_range_auto`,
 1 AS `ec_vch_range_auto`,
 1 AS `ec_ich_range_auto`,
 1 AS `samples_id_sample`,
 1 AS `samples_name_sample`,
 1 AS `samples_name_user`,
 1 AS `samples_t_manufactured__timestamp`,
 1 AS `samples_comment`,
 1 AS `samples_total_loading__mg_cm2`,
 1 AS `spots_id_spot`,
 1 AS `spots_spot_size__mm2`,
 1 AS `spots_pos_x__mm`,
 1 AS `spots_pos_y__mm`,
 1 AS `spots_comment`,
 1 AS `spots_total_loading__mg_cm2`,
 1 AS `cv_E_initial__VvsRE`,
 1 AS `cv_E_apex1__VvsRE`,
 1 AS `cv_E_apex2__VvsRE`,
 1 AS `cv_E_final__VvsRE`,
 1 AS `cv_scanrate__mV_s`,
 1 AS `cv_stepsize__mV`,
 1 AS `cv_cycles`,
 1 AS `geis_f_initial__Hz`,
 1 AS `geis_f_final__Hz`,
 1 AS `geis_I_dc__A`,
 1 AS `geis_I_amplitude__A`,
 1 AS `geis_R_initialguess__ohm`,
 1 AS `geis_points_per_decade`,
 1 AS `ghold_I_hold__A`,
 1 AS `ghold_t_hold__s`,
 1 AS `ghold_t_samplerate__s`,
 1 AS `peis_f_initial__Hz`,
 1 AS `peis_f_final__Hz`,
 1 AS `peis_E_dc__VvsRE`,
 1 AS `peis_E_amplitude__VvsRE`,
 1 AS `peis_R_initialguess__ohm`,
 1 AS `peis_points_per_decade`,
 1 AS `phold_E_hold__VvsRE`,
 1 AS `phold_t_hold__s`,
 1 AS `phold_t_samplerate__s`,
 1 AS `ppulse_E_hold1__VvsRE`,
 1 AS `ppulse_E_hold2__VvsRE`,
 1 AS `ppulse_t_hold1__s`,
 1 AS `ppulse_t_hold2__s`,
 1 AS `ppulse_t_samplerate__s`,
 1 AS `ppulse_cycles`,
 1 AS `gpulse_I_hold1__A`,
 1 AS `gpulse_I_hold2__A`,
 1 AS `gpulse_t_hold1__s`,
 1 AS `gpulse_t_hold2__s`,
 1 AS `gpulse_t_samplerate__s`,
 1 AS `gpulse_cycles`,
 1 AS `ramp_E_initial__VvsRE`,
 1 AS `ramp_E_final__VvsRE`,
 1 AS `ramp_scanrate__mV_s`,
 1 AS `ramp_stepsize__mV`,
 1 AS `ramp_cycles`,
 1 AS `fc_top_name_flow_cell`,
 1 AS `fc_top_name_flow_cell_name_user`,
 1 AS `fc_top_name_flow_cell_material`,
 1 AS `fc_top_name_flow_cell_A_opening_ideal__mm2`,
 1 AS `fc_top_name_flow_cell_A_opening_real__mm2`,
 1 AS `fc_top_name_flow_cell_manufacture_date`,
 1 AS `fc_top_name_flow_cell_CAD_file`,
 1 AS `fc_top_name_flow_cell_comment`,
 1 AS `fc_top_id_sealing`,
 1 AS `fc_top_id_sealing_name_user`,
 1 AS `fc_top_id_sealing_material`,
 1 AS `fc_top_id_sealing_A_sealing__mm2`,
 1 AS `fc_top_id_sealing_A_opening__mm2`,
 1 AS `fc_top_id_sealing_thickness__mm`,
 1 AS `fc_top_id_sealing_shaping_method`,
 1 AS `fc_top_id_sealing_comment`,
 1 AS `fc_top_id_PTL`,
 1 AS `fc_top_id_PTL_name_user`,
 1 AS `fc_top_id_PTL_material`,
 1 AS `fc_top_id_PTL_thickness__mm`,
 1 AS `fc_top_id_PTL_manufacturer`,
 1 AS `fc_top_id_PTL_A_PTL__mm2`,
 1 AS `fc_top_id_PTL_shaping_method`,
 1 AS `fc_top_id_PTL_comment`,
 1 AS `fc_bottom_name_flow_cell`,
 1 AS `fc_bottom_name_flow_cell_name_user`,
 1 AS `fc_bottom_name_flow_cell_material`,
 1 AS `fc_bottom_name_flow_cell_A_opening_ideal__mm2`,
 1 AS `fc_bottom_name_flow_cell_A_opening_real__mm2`,
 1 AS `fc_bottom_name_flow_cell_manufacture_date`,
 1 AS `fc_bottom_name_flow_cell_CAD_file`,
 1 AS `fc_bottom_name_flow_cell_comment`,
 1 AS `fc_bottom_id_sealing`,
 1 AS `fc_bottom_id_sealing_name_user`,
 1 AS `fc_bottom_id_sealing_material`,
 1 AS `fc_bottom_id_sealing_A_sealing__mm2`,
 1 AS `fc_bottom_id_sealing_A_opening__mm2`,
 1 AS `fc_bottom_id_sealing_thickness__mm`,
 1 AS `fc_bottom_id_sealing_shaping_method`,
 1 AS `fc_bottom_id_sealing_comment`,
 1 AS `fc_bottom_id_PTL`,
 1 AS `fc_bottom_id_PTL_name_user`,
 1 AS `fc_bottom_id_PTL_material`,
 1 AS `fc_bottom_id_PTL_thickness__mm`,
 1 AS `fc_bottom_id_PTL_manufacturer`,
 1 AS `fc_bottom_id_PTL_A_PTL__mm2`,
 1 AS `fc_bottom_id_PTL_shaping_method`,
 1 AS `fc_bottom_id_PTL_comment`,
 1 AS `fe_top_id_pump_in`,
 1 AS `fe_top_id_pump_in_manufacturer`,
 1 AS `fe_top_id_pump_in_model`,
 1 AS `fe_top_id_pump_in_device`,
 1 AS `fe_top_id_tubing_in`,
 1 AS `fe_top_id_tubing_in_name_tubing`,
 1 AS `fe_top_id_tubing_in_inner_diameter__mm`,
 1 AS `fe_top_id_tubing_in_color_code`,
 1 AS `fe_top_id_tubing_in_manufacturer`,
 1 AS `fe_top_id_tubing_in_model`,
 1 AS `fe_top_pump_rate_in__rpm`,
 1 AS `fe_top_id_pump_out`,
 1 AS `fe_top_id_pump_out_manufacturer`,
 1 AS `fe_top_id_pump_out_model`,
 1 AS `fe_top_id_pump_out_device`,
 1 AS `fe_top_id_tubing_out`,
 1 AS `fe_top_id_tubing_out_name_tubing`,
 1 AS `fe_top_id_tubing_out_inner_diameter__mm`,
 1 AS `fe_top_id_tubing_out_color_code`,
 1 AS `fe_top_id_tubing_out_manufacturer`,
 1 AS `fe_top_id_tubing_out_model`,
 1 AS `fe_top_pump_rate_out__rpm`,
 1 AS `fe_top_flow_rate_real__mul_min`,
 1 AS `fe_top_name_electrolyte`,
 1 AS `fe_top_c_electrolyte__mol_L`,
 1 AS `fe_top_T_electrolyte__degC`,
 1 AS `fe_bottom_id_pump_in`,
 1 AS `fe_bottom_id_pump_in_manufacturer`,
 1 AS `fe_bottom_id_pump_in_model`,
 1 AS `fe_bottom_id_pump_in_device`,
 1 AS `fe_bottom_id_tubing_in`,
 1 AS `fe_bottom_id_tubing_in_name_tubing`,
 1 AS `fe_bottom_id_tubing_in_inner_diameter__mm`,
 1 AS `fe_bottom_id_tubing_in_color_code`,
 1 AS `fe_bottom_id_tubing_in_manufacturer`,
 1 AS `fe_bottom_id_tubing_in_model`,
 1 AS `fe_bottom_pump_rate_in__rpm`,
 1 AS `fe_bottom_id_pump_out`,
 1 AS `fe_bottom_id_pump_out_manufacturer`,
 1 AS `fe_bottom_id_pump_out_model`,
 1 AS `fe_bottom_id_pump_out_device`,
 1 AS `fe_bottom_id_tubing_out`,
 1 AS `fe_bottom_id_tubing_out_name_tubing`,
 1 AS `fe_bottom_id_tubing_out_inner_diameter__mm`,
 1 AS `fe_bottom_id_tubing_out_color_code`,
 1 AS `fe_bottom_id_tubing_out_manufacturer`,
 1 AS `fe_bottom_id_tubing_out_model`,
 1 AS `fe_bottom_pump_rate_out__rpm`,
 1 AS `fe_bottom_flow_rate_real__mul_min`,
 1 AS `fe_bottom_name_electrolyte`,
 1 AS `fe_bottom_c_electrolyte__mol_L`,
 1 AS `fe_bottom_T_electrolyte__degC`,
 1 AS `fg_top_Arring_name_gas`,
 1 AS `fg_top_Arring_flow_rate__mL_min`,
 1 AS `fg_top_purgevial_name_gas`,
 1 AS `fg_top_purgevial_flow_rate__mL_min`,
 1 AS `fg_top_main_name_gas`,
 1 AS `fg_top_main_flow_rate__mL_min`,
 1 AS `fg_bottom_Arring_name_gas`,
 1 AS `fg_bottom_Arring_flow_rate__mL_min`,
 1 AS `fg_bottom_purgevial_name_gas`,
 1 AS `fg_bottom_purgevial_flow_rate__mL_min`,
 1 AS `fg_bottom_main_name_gas`,
 1 AS `fg_bottom_main_flow_rate__mL_min`,
 1 AS `n_product_of_interest_simps__mol`,
 1 AS `n_product_of_interest_trapz__mol`,
 1 AS `S_number_simps`,
 1 AS `S_number_trapz`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `documentation_columns`
--

DROP TABLE IF EXISTS `documentation_columns`;
/*!50001 DROP VIEW IF EXISTS `documentation_columns`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `documentation_columns` AS SELECT 
 1 AS `name_table`,
 1 AS `name_column`,
 1 AS `name_inserter`,
 1 AS `comment`,
 1 AS `name_axislabel__latex`,
 1 AS `table_type`,
 1 AS `data_type`,
 1 AS `max_length`,
 1 AS `precision`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `documentation_tables`
--

DROP TABLE IF EXISTS `documentation_tables`;
/*!50001 DROP VIEW IF EXISTS `documentation_tables`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `documentation_tables` AS SELECT 
 1 AS `name_table`,
 1 AS `comment_table`,
 1 AS `number_rows`,
 1 AS `amount_data`,
 1 AS `table_type`,
 1 AS `name_base_table`*/;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `dummy_data_icpms_sfc_batch_analysis`
--

DROP TABLE IF EXISTS `dummy_data_icpms_sfc_batch_analysis`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `dummy_data_icpms_sfc_batch_analysis` (
  `id_data_icpms` int NOT NULL COMMENT 'index of icpms experiment',
  PRIMARY KEY (`id_data_icpms`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='required for view data_icpms_sfc_batch_analysis';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ec_reactions`
--

DROP TABLE IF EXISTS `ec_reactions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ec_reactions` (
  `name_reaction` varchar(45) NOT NULL COMMENT 'identifier of the electrochemical reaction',
  `name_product_of_interest` varchar(45) DEFAULT NULL COMMENT 'name of the electrochemical reaction product of interest',
  `number_electrons` int DEFAULT NULL COMMENT 'number of released electrons per product of interest. Positive for anodic oxidation reactions, negative for cathodic reduction reactions.',
  PRIMARY KEY (`name_reaction`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='holding informations for electrochemical reactions';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `electrolytes`
--

DROP TABLE IF EXISTS `electrolytes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `electrolytes` (
  `name_electrolyte` varchar(45) NOT NULL COMMENT 'name of the used electrolyte. So far only unary electrolytes (one component in DI water) is supported. File a feature request if needed.',
  PRIMARY KEY (`name_electrolyte`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Inventory list of available electrolyte salts';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `elements`
--

DROP TABLE IF EXISTS `elements`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `elements` (
  `element` varchar(2) NOT NULL COMMENT 'two-letter element code according to periodic table',
  `atomic_number` int NOT NULL COMMENT 'atomic number of element',
  `M__g_mol` float NOT NULL COMMENT 'molmasses as published https://www.nist.gov/system/files/documents/2022/08/30/NIST%20periodic%20table%20--%20August%202022.pdf',
  PRIMARY KEY (`element`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='holding information of elements of periodic table';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `exp_compression`
--

DROP TABLE IF EXISTS `exp_compression`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `exp_compression` (
  `id_exp_sfc` int NOT NULL COMMENT 'index for each comprssion experiment connection to exp_sfc',
  `linaxis_speed__mm_s` float DEFAULT NULL COMMENT 'Speed of the linear axis in mm per s',
  PRIMARY KEY (`id_exp_sfc`),
  CONSTRAINT `FK_exp_compression_exp_sfc` FOREIGN KEY (`id_exp_sfc`) REFERENCES `exp_sfc` (`id_exp_sfc`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='parameter of compression experiments performed with sfc table';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `exp_ec`
--

DROP TABLE IF EXISTS `exp_ec`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `exp_ec` (
  `id_exp_sfc` int NOT NULL COMMENT 'index for each sfc experiment connection to exp_sfc',
  `name_technique` varchar(15) NOT NULL COMMENT 'name of the ec technique as selected in the SFC software (cv and advanced cv are combined in one table, galvanostatic and potentiostatic techniques are separated to ensure correct units in column name)',
  `R_u__ohm` float DEFAULT NULL COMMENT 'uncompensated resistance value used to correct for iR drop within the measurement. R_u__ohm * iR_corr_in_situ__percent/100 gives the resistance value send to the potentiostat. R_u__ohm * (1-iR_corr_in_situ__percent/100) gives the resistance value need to be corrected for post measurement to ensure full compensation',
  `iR_corr_in_situ__percent` float DEFAULT NULL COMMENT 'percentage of the insitu iR drop correction performed within the experiment. R_u__ohm * iR_corr_in_situ__percent/100 gives the resistance value send to the potentiostat. R_u__ohm * (1-iR_corr_in_situ__percent/100) gives the resistance value need to be corrected for post measurement to ensure full compensation',
  `R_u_postdetermined__ohm` float DEFAULT NULL COMMENT ' R_u__ohm as determined by tools_ec.update_R_u__ohm',
  `R_u_determining_exp_ec` int DEFAULT NULL COMMENT 'id_exp_ec of the corresponding eis experiment which was used to determine R_u',
  `R_u_determining_updated` datetime(6) DEFAULT NULL COMMENT 'date of the last update of R_u__ohm, as performed by tools_ec.update_R_u__ohm',
  `E_RE__VvsRHE` float DEFAULT NULL COMMENT 'potential of the reference electrode vs. RHE. Used to reference measured WE potential against RHE.',
  `name_RE` varchar(40) NOT NULL COMMENT 'name of the used reference electrode',
  `name_CE` varchar(40) NOT NULL COMMENT 'name of the used counter electrode',
  `name_device` varchar(40) NOT NULL COMMENT 'name of the potentiostat (gamry, biologic,...)',
  `id_control_mode` int NOT NULL COMMENT 'potentiostatic or galvanostatic control mode of the potentiostat',
  `id_ie_range` int NOT NULL COMMENT 'see gamry documentation',
  `id_vch_range` int NOT NULL COMMENT 'see gamry documentation',
  `id_ich_range` int NOT NULL COMMENT 'see gamry documentation',
  `id_vch_filter` int NOT NULL COMMENT 'see gamry documentation',
  `id_ich_filter` int NOT NULL COMMENT 'see gamry documentation',
  `id_ca_speed` int NOT NULL COMMENT 'see gamry documentation',
  `id_ie_stability` int NOT NULL COMMENT 'see gamry documentation',
  `id_sampling_mode` int NOT NULL COMMENT 'see gamry documentation',
  `ie_range_auto` tinyint(1) NOT NULL COMMENT 'is ie range automatically adjusted by potentiostat? Further info see gamry documentation',
  `vch_range_auto` tinyint(1) NOT NULL COMMENT 'is vch range automatically adjusted by potentiostat? Further info see gamry documentation',
  `ich_range_auto` tinyint(1) NOT NULL COMMENT 'is ich range automatically adjusted by potentiostat? Further info see gamry documentation',
  PRIMARY KEY (`id_exp_sfc`),
  KEY `FK_exp_ec_control_mode` (`id_control_mode`),
  KEY `FK_exp_ec_ie_range` (`id_ie_range`),
  KEY `FK_exp_ec_vch_range` (`id_vch_range`),
  KEY `FK_exp_ec_ich_range` (`id_ich_range`),
  KEY `FK_exp_ec_vch_filter` (`id_vch_filter`),
  KEY `FK_exp_ec_ich_filter` (`id_ich_filter`),
  KEY `FK_exp_ec_ca_speed` (`id_ca_speed`),
  KEY `FK_exp_ec_ie_stability` (`id_ie_stability`),
  KEY `FK_exp_ec_sampling_mode` (`id_sampling_mode`),
  KEY `FK_exp_ec_RE` (`name_RE`),
  KEY `FK_exp_ec_CE` (`name_CE`),
  KEY `FK_exp_ec_R_u_determining_id_exp_ec_idx` (`R_u_determining_exp_ec`),
  KEY `FK_exp_ec_techniques_idx` (`name_technique`) /*!80000 INVISIBLE */,
  KEY `INDEX_id_exp_sfc_name_technique` (`id_exp_sfc`,`name_technique`),
  CONSTRAINT `FK_exp_ec_ca_speed` FOREIGN KEY (`id_ca_speed`) REFERENCES `gamry_set_ca_speed` (`id_ca_speed`),
  CONSTRAINT `FK_exp_ec_CE` FOREIGN KEY (`name_CE`) REFERENCES `counter_electrodes` (`name_CE`) ON UPDATE CASCADE,
  CONSTRAINT `FK_exp_ec_control_mode` FOREIGN KEY (`id_control_mode`) REFERENCES `gamry_set_control_mode` (`id_control_mode`),
  CONSTRAINT `FK_exp_ec_ich_filter` FOREIGN KEY (`id_ich_filter`) REFERENCES `gamry_set_ich_filter` (`id_ich_filter`),
  CONSTRAINT `FK_exp_ec_ich_range` FOREIGN KEY (`id_ich_range`) REFERENCES `gamry_set_ich_range` (`id_ich_range`),
  CONSTRAINT `FK_exp_ec_id_exp_sfc` FOREIGN KEY (`id_exp_sfc`) REFERENCES `exp_sfc` (`id_exp_sfc`),
  CONSTRAINT `FK_exp_ec_ie_range` FOREIGN KEY (`id_ie_range`) REFERENCES `gamry_set_ie_range` (`id_ie_range`),
  CONSTRAINT `FK_exp_ec_ie_stability` FOREIGN KEY (`id_ie_stability`) REFERENCES `gamry_set_ie_stability` (`id_ie_stability`),
  CONSTRAINT `FK_exp_ec_R_u_determining_id_exp_ec` FOREIGN KEY (`R_u_determining_exp_ec`) REFERENCES `exp_ec` (`id_exp_sfc`),
  CONSTRAINT `FK_exp_ec_RE` FOREIGN KEY (`name_RE`) REFERENCES `reference_electrodes` (`name_RE`) ON UPDATE CASCADE,
  CONSTRAINT `FK_exp_ec_sampling_mode` FOREIGN KEY (`id_sampling_mode`) REFERENCES `gamry_set_sampling_mode` (`id_sampling_mode`),
  CONSTRAINT `FK_exp_ec_techniques` FOREIGN KEY (`name_technique`) REFERENCES `exp_ec_techniques` (`name_technique`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `FK_exp_ec_vch_filter` FOREIGN KEY (`id_vch_filter`) REFERENCES `gamry_set_vch_filter` (`id_vch_filter`),
  CONSTRAINT `FK_exp_ec_vch_range` FOREIGN KEY (`id_vch_range`) REFERENCES `gamry_set_vch_range` (`id_vch_range`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='parameter of electrochemical experiments. For parameters which can hold more than one value per experiment (for instance multiple gas flows in one experiment) are located in other tables connected to the exp_ec table via the id_exp_ec. Same holds true for different ec techniques such as CV, PEIS , GEIS,... with technique specific parameters. All parameters combined in one table can be found in the corresponding view "exp_ec_expanded". It is recommended to use this one for selecting data to circumvent multiple join statements in the select query.';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `exp_ec_cv`
--

DROP TABLE IF EXISTS `exp_ec_cv`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `exp_ec_cv` (
  `id_exp_sfc` int NOT NULL COMMENT 'connects technique (CV) specific parameters to experiment parameters (exp_ec)',
  `name_technique` varchar(15) NOT NULL DEFAULT 'exp_ec_cv' COMMENT 'name of the technique - required to foreign key on exp_ec',
  `E_initial__VvsRE` float NOT NULL COMMENT 'inital potential of the CV cycle against reference electrode potential',
  `E_apex1__VvsRE` float NOT NULL COMMENT 'first potential limit (upper or lower) of the CV cycle against reference electrode potential',
  `E_apex2__VvsRE` float NOT NULL COMMENT 'second potential limit (upper or lower) of the CV cycle against reference electrode potential',
  `E_final__VvsRE` float NOT NULL COMMENT 'final potential of the CV cycle against reference electrode potential',
  `scanrate__mV_s` float NOT NULL COMMENT 'potential scanrate of the CV experiment in milli Volt per second',
  `stepsize__mV` float NOT NULL COMMENT 'potential stepsize of the CV',
  `cycles` int NOT NULL COMMENT 'number of cycles',
  PRIMARY KEY (`id_exp_sfc`,`name_technique`),
  UNIQUE KEY `id_exp_ec_UNIQUE` (`id_exp_sfc`),
  KEY `FK_exp_ec_cv_name_technique_idx` (`name_technique`),
  CONSTRAINT `FK_exp_ec_cv` FOREIGN KEY (`id_exp_sfc`, `name_technique`) REFERENCES `exp_ec` (`id_exp_sfc`, `name_technique`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `FK_is_exp_ec_cv_name_technique` FOREIGN KEY (`name_technique`) REFERENCES `is_exp_ec_cv` (`name_technique`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='technique specific parameters for cyclic voltammetry (CV)';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `exp_ec_datasets`
--

DROP TABLE IF EXISTS `exp_ec_datasets`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `exp_ec_datasets` (
  `id_exp_ec_dataset` int NOT NULL AUTO_INCREMENT COMMENT 'id of the ec dataset',
  `name_exp_ec_dataset` varchar(145) DEFAULT NULL COMMENT 'name of the ec dataset. Can be used to sort experiments according to their name.',
  PRIMARY KEY (`id_exp_ec_dataset`)
) ENGINE=InnoDB AUTO_INCREMENT=159 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='table of all ec datasets';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `exp_ec_datasets_definer`
--

DROP TABLE IF EXISTS `exp_ec_datasets_definer`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `exp_ec_datasets_definer` (
  `id_exp_ec_dataset` int NOT NULL COMMENT 'id of the ec dataset',
  `id_exp_sfc` int NOT NULL COMMENT 'id of the single ec experiment',
  PRIMARY KEY (`id_exp_ec_dataset`,`id_exp_sfc`),
  KEY `FK_exp_ec_datasets_id_exp_ec_idx` (`id_exp_sfc`),
  CONSTRAINT `FK_exp_ec_datasets_definer_id_exp_ec` FOREIGN KEY (`id_exp_sfc`) REFERENCES `exp_ec` (`id_exp_sfc`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `FK_exp_ec_datasets_definer_id_exp_ec_dataset` FOREIGN KEY (`id_exp_ec_dataset`) REFERENCES `exp_ec_datasets` (`id_exp_ec_dataset`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='one ec dataset can consist of multiple exp_ec. This table is defining the n-n relationship';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Temporary view structure for view `exp_ec_expanded`
--

DROP TABLE IF EXISTS `exp_ec_expanded`;
/*!50001 DROP VIEW IF EXISTS `exp_ec_expanded`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `exp_ec_expanded` AS SELECT 
 1 AS `id_exp_sfc`,
 1 AS `name_user`,
 1 AS `name_setup_sfc`,
 1 AS `name_setup_sfc_alias`,
 1 AS `name_setup_sfc_feature`,
 1 AS `name_setup_sfc_type`,
 1 AS `t_start__timestamp`,
 1 AS `t_end__timestamp`,
 1 AS `rawdata_path`,
 1 AS `rawdata_computer`,
 1 AS `id_ML`,
 1 AS `id_ML_technique`,
 1 AS `id_sample`,
 1 AS `id_spot`,
 1 AS `force__N`,
 1 AS `T_stage__degC`,
 1 AS `interrupted`,
 1 AS `labview_sfc_version`,
 1 AS `db_version`,
 1 AS `comment`,
 1 AS `ec_name_technique`,
 1 AS `ec_R_u__ohm`,
 1 AS `ec_iR_corr_in_situ__percent`,
 1 AS `ec_R_u_determining_exp_ec`,
 1 AS `ec_E_RE__VvsRHE`,
 1 AS `ec_name_RE`,
 1 AS `ec_name_RE_material`,
 1 AS `ec_name_RE_manufacturer`,
 1 AS `ec_name_RE_model`,
 1 AS `ec_name_CE`,
 1 AS `ec_name_CE_material`,
 1 AS `ec_name_CE_manufacturer`,
 1 AS `ec_name_CE_model`,
 1 AS `ec_name_device`,
 1 AS `ec_id_control_mode`,
 1 AS `ec_id_ie_range`,
 1 AS `ec_id_vch_range`,
 1 AS `ec_id_ich_range`,
 1 AS `ec_id_vch_filter`,
 1 AS `ec_id_ich_filter`,
 1 AS `ec_id_ca_speed`,
 1 AS `ec_id_ie_stability`,
 1 AS `ec_id_sampling_mode`,
 1 AS `ec_ie_range_auto`,
 1 AS `ec_vch_range_auto`,
 1 AS `ec_ich_range_auto`,
 1 AS `samples_id_sample`,
 1 AS `samples_name_sample`,
 1 AS `samples_name_user`,
 1 AS `samples_t_manufactured__timestamp`,
 1 AS `samples_comment`,
 1 AS `samples_total_loading__mg_cm2`,
 1 AS `spots_id_spot`,
 1 AS `spots_spot_size__mm2`,
 1 AS `spots_pos_x__mm`,
 1 AS `spots_pos_y__mm`,
 1 AS `spots_comment`,
 1 AS `spots_total_loading__mg_cm2`,
 1 AS `cv_E_initial__VvsRE`,
 1 AS `cv_E_apex1__VvsRE`,
 1 AS `cv_E_apex2__VvsRE`,
 1 AS `cv_E_final__VvsRE`,
 1 AS `cv_scanrate__mV_s`,
 1 AS `cv_stepsize__mV`,
 1 AS `cv_cycles`,
 1 AS `geis_f_initial__Hz`,
 1 AS `geis_f_final__Hz`,
 1 AS `geis_I_dc__A`,
 1 AS `geis_I_amplitude__A`,
 1 AS `geis_R_initialguess__ohm`,
 1 AS `geis_points_per_decade`,
 1 AS `ghold_I_hold__A`,
 1 AS `ghold_t_hold__s`,
 1 AS `ghold_t_samplerate__s`,
 1 AS `peis_f_initial__Hz`,
 1 AS `peis_f_final__Hz`,
 1 AS `peis_E_dc__VvsRE`,
 1 AS `peis_E_amplitude__VvsRE`,
 1 AS `peis_R_initialguess__ohm`,
 1 AS `peis_points_per_decade`,
 1 AS `phold_E_hold__VvsRE`,
 1 AS `phold_t_hold__s`,
 1 AS `phold_t_samplerate__s`,
 1 AS `ppulse_E_hold1__VvsRE`,
 1 AS `ppulse_E_hold2__VvsRE`,
 1 AS `ppulse_t_hold1__s`,
 1 AS `ppulse_t_hold2__s`,
 1 AS `ppulse_t_samplerate__s`,
 1 AS `ppulse_cycles`,
 1 AS `gpulse_I_hold1__A`,
 1 AS `gpulse_I_hold2__A`,
 1 AS `gpulse_t_hold1__s`,
 1 AS `gpulse_t_hold2__s`,
 1 AS `gpulse_t_samplerate__s`,
 1 AS `gpulse_cycles`,
 1 AS `ramp_E_initial__VvsRE`,
 1 AS `ramp_E_final__VvsRE`,
 1 AS `ramp_scanrate__mV_s`,
 1 AS `ramp_stepsize__mV`,
 1 AS `ramp_cycles`,
 1 AS `fc_top_name_flow_cell`,
 1 AS `fc_top_name_flow_cell_name_user`,
 1 AS `fc_top_name_flow_cell_material`,
 1 AS `fc_top_name_flow_cell_A_opening_ideal__mm2`,
 1 AS `fc_top_name_flow_cell_A_opening_real__mm2`,
 1 AS `fc_top_name_flow_cell_manufacture_date`,
 1 AS `fc_top_name_flow_cell_CAD_file`,
 1 AS `fc_top_name_flow_cell_comment`,
 1 AS `fc_top_id_sealing`,
 1 AS `fc_top_id_sealing_name_user`,
 1 AS `fc_top_id_sealing_material`,
 1 AS `fc_top_id_sealing_A_sealing__mm2`,
 1 AS `fc_top_id_sealing_A_opening__mm2`,
 1 AS `fc_top_id_sealing_thickness__mm`,
 1 AS `fc_top_id_sealing_shaping_method`,
 1 AS `fc_top_id_sealing_comment`,
 1 AS `fc_top_id_PTL`,
 1 AS `fc_top_id_PTL_name_user`,
 1 AS `fc_top_id_PTL_material`,
 1 AS `fc_top_id_PTL_thickness__mm`,
 1 AS `fc_top_id_PTL_manufacturer`,
 1 AS `fc_top_id_PTL_A_PTL__mm2`,
 1 AS `fc_top_id_PTL_shaping_method`,
 1 AS `fc_top_id_PTL_comment`,
 1 AS `fc_bottom_name_flow_cell`,
 1 AS `fc_bottom_name_flow_cell_name_user`,
 1 AS `fc_bottom_name_flow_cell_material`,
 1 AS `fc_bottom_name_flow_cell_A_opening_ideal__mm2`,
 1 AS `fc_bottom_name_flow_cell_A_opening_real__mm2`,
 1 AS `fc_bottom_name_flow_cell_manufacture_date`,
 1 AS `fc_bottom_name_flow_cell_CAD_file`,
 1 AS `fc_bottom_name_flow_cell_comment`,
 1 AS `fc_bottom_id_sealing`,
 1 AS `fc_bottom_id_sealing_name_user`,
 1 AS `fc_bottom_id_sealing_material`,
 1 AS `fc_bottom_id_sealing_A_sealing__mm2`,
 1 AS `fc_bottom_id_sealing_A_opening__mm2`,
 1 AS `fc_bottom_id_sealing_thickness__mm`,
 1 AS `fc_bottom_id_sealing_shaping_method`,
 1 AS `fc_bottom_id_sealing_comment`,
 1 AS `fc_bottom_id_PTL`,
 1 AS `fc_bottom_id_PTL_name_user`,
 1 AS `fc_bottom_id_PTL_material`,
 1 AS `fc_bottom_id_PTL_thickness__mm`,
 1 AS `fc_bottom_id_PTL_manufacturer`,
 1 AS `fc_bottom_id_PTL_A_PTL__mm2`,
 1 AS `fc_bottom_id_PTL_shaping_method`,
 1 AS `fc_bottom_id_PTL_comment`,
 1 AS `fe_top_id_pump_in`,
 1 AS `fe_top_id_pump_in_manufacturer`,
 1 AS `fe_top_id_pump_in_model`,
 1 AS `fe_top_id_pump_in_device`,
 1 AS `fe_top_id_tubing_in`,
 1 AS `fe_top_id_tubing_in_name_tubing`,
 1 AS `fe_top_id_tubing_in_inner_diameter__mm`,
 1 AS `fe_top_id_tubing_in_color_code`,
 1 AS `fe_top_id_tubing_in_manufacturer`,
 1 AS `fe_top_id_tubing_in_model`,
 1 AS `fe_top_pump_rate_in__rpm`,
 1 AS `fe_top_id_pump_out`,
 1 AS `fe_top_id_pump_out_manufacturer`,
 1 AS `fe_top_id_pump_out_model`,
 1 AS `fe_top_id_pump_out_device`,
 1 AS `fe_top_id_tubing_out`,
 1 AS `fe_top_id_tubing_out_name_tubing`,
 1 AS `fe_top_id_tubing_out_inner_diameter__mm`,
 1 AS `fe_top_id_tubing_out_color_code`,
 1 AS `fe_top_id_tubing_out_manufacturer`,
 1 AS `fe_top_id_tubing_out_model`,
 1 AS `fe_top_pump_rate_out__rpm`,
 1 AS `fe_top_flow_rate_real__mul_min`,
 1 AS `fe_top_name_electrolyte`,
 1 AS `fe_top_c_electrolyte__mol_L`,
 1 AS `fe_top_T_electrolyte__degC`,
 1 AS `fe_bottom_id_pump_in`,
 1 AS `fe_bottom_id_pump_in_manufacturer`,
 1 AS `fe_bottom_id_pump_in_model`,
 1 AS `fe_bottom_id_pump_in_device`,
 1 AS `fe_bottom_id_tubing_in`,
 1 AS `fe_bottom_id_tubing_in_name_tubing`,
 1 AS `fe_bottom_id_tubing_in_inner_diameter__mm`,
 1 AS `fe_bottom_id_tubing_in_color_code`,
 1 AS `fe_bottom_id_tubing_in_manufacturer`,
 1 AS `fe_bottom_id_tubing_in_model`,
 1 AS `fe_bottom_pump_rate_in__rpm`,
 1 AS `fe_bottom_id_pump_out`,
 1 AS `fe_bottom_id_pump_out_manufacturer`,
 1 AS `fe_bottom_id_pump_out_model`,
 1 AS `fe_bottom_id_pump_out_device`,
 1 AS `fe_bottom_id_tubing_out`,
 1 AS `fe_bottom_id_tubing_out_name_tubing`,
 1 AS `fe_bottom_id_tubing_out_inner_diameter__mm`,
 1 AS `fe_bottom_id_tubing_out_color_code`,
 1 AS `fe_bottom_id_tubing_out_manufacturer`,
 1 AS `fe_bottom_id_tubing_out_model`,
 1 AS `fe_bottom_pump_rate_out__rpm`,
 1 AS `fe_bottom_flow_rate_real__mul_min`,
 1 AS `fe_bottom_name_electrolyte`,
 1 AS `fe_bottom_c_electrolyte__mol_L`,
 1 AS `fe_bottom_T_electrolyte__degC`,
 1 AS `fg_top_Arring_name_gas`,
 1 AS `fg_top_Arring_flow_rate__mL_min`,
 1 AS `fg_top_purgevial_name_gas`,
 1 AS `fg_top_purgevial_flow_rate__mL_min`,
 1 AS `fg_top_main_name_gas`,
 1 AS `fg_top_main_flow_rate__mL_min`,
 1 AS `fg_bottom_Arring_name_gas`,
 1 AS `fg_bottom_Arring_flow_rate__mL_min`,
 1 AS `fg_bottom_purgevial_name_gas`,
 1 AS `fg_bottom_purgevial_flow_rate__mL_min`,
 1 AS `fg_bottom_main_name_gas`,
 1 AS `fg_bottom_main_flow_rate__mL_min`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `exp_ec_expanded_old`
--

DROP TABLE IF EXISTS `exp_ec_expanded_old`;
/*!50001 DROP VIEW IF EXISTS `exp_ec_expanded_old`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `exp_ec_expanded_old` AS SELECT 
 1 AS `id_exp_sfc`,
 1 AS `name_user`,
 1 AS `name_setup_sfc`,
 1 AS `name_setup_sfc_alias`,
 1 AS `name_setup_sfc_feature`,
 1 AS `name_setup_sfc_type`,
 1 AS `t_start__timestamp`,
 1 AS `rawdata_path`,
 1 AS `rawdata_computer`,
 1 AS `id_ML`,
 1 AS `id_ML_technique`,
 1 AS `id_sample`,
 1 AS `id_spot`,
 1 AS `force__N`,
 1 AS `T_stage__degC`,
 1 AS `interrupted`,
 1 AS `labview_sfc_version`,
 1 AS `db_version`,
 1 AS `comment`,
 1 AS `t_duration__s`,
 1 AS `t_end__timestamp`,
 1 AS `ec_name_technique`,
 1 AS `ec_R_u__ohm`,
 1 AS `ec_iR_corr_in_situ__percent`,
 1 AS `ec_R_u_determining_exp_ec`,
 1 AS `ec_E_RE__VvsRHE`,
 1 AS `ec_name_RE`,
 1 AS `ec_name_RE_material`,
 1 AS `ec_name_RE_manufacturer`,
 1 AS `ec_name_RE_model`,
 1 AS `ec_name_CE`,
 1 AS `ec_name_CE_material`,
 1 AS `ec_name_CE_manufacturer`,
 1 AS `ec_name_CE_model`,
 1 AS `ec_name_device`,
 1 AS `ec_id_control_mode`,
 1 AS `ec_id_ie_range`,
 1 AS `ec_id_vch_range`,
 1 AS `ec_id_ich_range`,
 1 AS `ec_id_vch_filter`,
 1 AS `ec_id_ich_filter`,
 1 AS `ec_id_ca_speed`,
 1 AS `ec_id_ie_stability`,
 1 AS `ec_id_sampling_mode`,
 1 AS `ec_ie_range_auto`,
 1 AS `ec_vch_range_auto`,
 1 AS `ec_ich_range_auto`,
 1 AS `samples_id_sample`,
 1 AS `samples_name_sample`,
 1 AS `samples_name_user`,
 1 AS `samples_t_manufactured__timestamp`,
 1 AS `samples_comment`,
 1 AS `samples_total_loading__mg_cm2`,
 1 AS `spots_id_spot`,
 1 AS `spots_spot_size__mm2`,
 1 AS `spots_pos_x__mm`,
 1 AS `spots_pos_y__mm`,
 1 AS `spots_comment`,
 1 AS `spots_total_loading__mg_cm2`,
 1 AS `cv_E_initial__VvsRE`,
 1 AS `cv_E_apex1__VvsRE`,
 1 AS `cv_E_apex2__VvsRE`,
 1 AS `cv_E_final__VvsRE`,
 1 AS `cv_scanrate__mV_s`,
 1 AS `cv_stepsize__mV`,
 1 AS `cv_cycles`,
 1 AS `geis_f_initial__Hz`,
 1 AS `geis_f_final__Hz`,
 1 AS `geis_I_dc__A`,
 1 AS `geis_I_amplitude__A`,
 1 AS `geis_R_initialguess__ohm`,
 1 AS `geis_points_per_decade`,
 1 AS `ghold_I_hold__A`,
 1 AS `ghold_t_hold__s`,
 1 AS `ghold_t_samplerate__s`,
 1 AS `peis_f_initial__Hz`,
 1 AS `peis_f_final__Hz`,
 1 AS `peis_E_dc__VvsRE`,
 1 AS `peis_E_amplitude__VvsRE`,
 1 AS `peis_R_initialguess__ohm`,
 1 AS `peis_points_per_decade`,
 1 AS `phold_E_hold__VvsRE`,
 1 AS `phold_t_hold__s`,
 1 AS `phold_t_samplerate__s`,
 1 AS `ppulse_E_hold1__VvsRE`,
 1 AS `ppulse_E_hold2__VvsRE`,
 1 AS `ppulse_t_hold1__s`,
 1 AS `ppulse_t_hold2__s`,
 1 AS `ppulse_t_samplerate__s`,
 1 AS `ppulse_cycles`,
 1 AS `gpulse_I_hold1__A`,
 1 AS `gpulse_I_hold2__A`,
 1 AS `gpulse_t_hold1__s`,
 1 AS `gpulse_t_hold2__s`,
 1 AS `gpulse_t_samplerate__s`,
 1 AS `gpulse_cycles`,
 1 AS `ramp_E_initial__VvsRE`,
 1 AS `ramp_E_final__VvsRE`,
 1 AS `ramp_scanrate__mV_s`,
 1 AS `ramp_stepsize__mV`,
 1 AS `ramp_cycles`,
 1 AS `fc_top_name_flow_cell`,
 1 AS `fc_top_name_flow_cell_name_user`,
 1 AS `fc_top_name_flow_cell_material`,
 1 AS `fc_top_name_flow_cell_A_opening_ideal__mm2`,
 1 AS `fc_top_name_flow_cell_A_opening_real__mm2`,
 1 AS `fc_top_name_flow_cell_manufacture_date`,
 1 AS `fc_top_name_flow_cell_CAD_file`,
 1 AS `fc_top_name_flow_cell_comment`,
 1 AS `fc_top_id_sealing`,
 1 AS `fc_top_id_sealing_name_user`,
 1 AS `fc_top_id_sealing_material`,
 1 AS `fc_top_id_sealing_A_sealing__mm2`,
 1 AS `fc_top_id_sealing_A_opening__mm2`,
 1 AS `fc_top_id_sealing_thickness__mm`,
 1 AS `fc_top_id_sealing_shaping_method`,
 1 AS `fc_top_id_sealing_comment`,
 1 AS `fc_top_id_PTL`,
 1 AS `fc_top_id_PTL_name_user`,
 1 AS `fc_top_id_PTL_material`,
 1 AS `fc_top_id_PTL_thickness__mm`,
 1 AS `fc_top_id_PTL_manufacturer`,
 1 AS `fc_top_id_PTL_A_PTL__mm2`,
 1 AS `fc_top_id_PTL_shaping_method`,
 1 AS `fc_top_id_PTL_comment`,
 1 AS `fc_bottom_name_flow_cell`,
 1 AS `fc_bottom_name_flow_cell_name_user`,
 1 AS `fc_bottom_name_flow_cell_material`,
 1 AS `fc_bottom_name_flow_cell_A_opening_ideal__mm2`,
 1 AS `fc_bottom_name_flow_cell_A_opening_real__mm2`,
 1 AS `fc_bottom_name_flow_cell_manufacture_date`,
 1 AS `fc_bottom_name_flow_cell_CAD_file`,
 1 AS `fc_bottom_name_flow_cell_comment`,
 1 AS `fc_bottom_id_sealing`,
 1 AS `fc_bottom_id_sealing_name_user`,
 1 AS `fc_bottom_id_sealing_material`,
 1 AS `fc_bottom_id_sealing_A_sealing__mm2`,
 1 AS `fc_bottom_id_sealing_A_opening__mm2`,
 1 AS `fc_bottom_id_sealing_thickness__mm`,
 1 AS `fc_bottom_id_sealing_shaping_method`,
 1 AS `fc_bottom_id_sealing_comment`,
 1 AS `fc_bottom_id_PTL`,
 1 AS `fc_bottom_id_PTL_name_user`,
 1 AS `fc_bottom_id_PTL_material`,
 1 AS `fc_bottom_id_PTL_thickness__mm`,
 1 AS `fc_bottom_id_PTL_manufacturer`,
 1 AS `fc_bottom_id_PTL_A_PTL__mm2`,
 1 AS `fc_bottom_id_PTL_shaping_method`,
 1 AS `fc_bottom_id_PTL_comment`,
 1 AS `fe_top_id_pump_in`,
 1 AS `fe_top_id_pump_in_manufacturer`,
 1 AS `fe_top_id_pump_in_model`,
 1 AS `fe_top_id_pump_in_device`,
 1 AS `fe_top_id_tubing_in`,
 1 AS `fe_top_id_tubing_in_name_tubing`,
 1 AS `fe_top_id_tubing_in_inner_diameter__mm`,
 1 AS `fe_top_id_tubing_in_color_code`,
 1 AS `fe_top_id_tubing_in_manufacturer`,
 1 AS `fe_top_id_tubing_in_model`,
 1 AS `fe_top_pump_rate_in__rpm`,
 1 AS `fe_top_id_pump_out`,
 1 AS `fe_top_id_pump_out_manufacturer`,
 1 AS `fe_top_id_pump_out_model`,
 1 AS `fe_top_id_pump_out_device`,
 1 AS `fe_top_id_tubing_out`,
 1 AS `fe_top_id_tubing_out_name_tubing`,
 1 AS `fe_top_id_tubing_out_inner_diameter__mm`,
 1 AS `fe_top_id_tubing_out_color_code`,
 1 AS `fe_top_id_tubing_out_manufacturer`,
 1 AS `fe_top_id_tubing_out_model`,
 1 AS `fe_top_pump_rate_out__rpm`,
 1 AS `fe_top_flow_rate_real__mul_min`,
 1 AS `fe_top_name_electrolyte`,
 1 AS `fe_top_c_electrolyte__mol_L`,
 1 AS `fe_top_T_electrolyte__degC`,
 1 AS `fe_bottom_id_pump_in`,
 1 AS `fe_bottom_id_pump_in_manufacturer`,
 1 AS `fe_bottom_id_pump_in_model`,
 1 AS `fe_bottom_id_pump_in_device`,
 1 AS `fe_bottom_id_tubing_in`,
 1 AS `fe_bottom_id_tubing_in_name_tubing`,
 1 AS `fe_bottom_id_tubing_in_inner_diameter__mm`,
 1 AS `fe_bottom_id_tubing_in_color_code`,
 1 AS `fe_bottom_id_tubing_in_manufacturer`,
 1 AS `fe_bottom_id_tubing_in_model`,
 1 AS `fe_bottom_pump_rate_in__rpm`,
 1 AS `fe_bottom_id_pump_out`,
 1 AS `fe_bottom_id_pump_out_manufacturer`,
 1 AS `fe_bottom_id_pump_out_model`,
 1 AS `fe_bottom_id_pump_out_device`,
 1 AS `fe_bottom_id_tubing_out`,
 1 AS `fe_bottom_id_tubing_out_name_tubing`,
 1 AS `fe_bottom_id_tubing_out_inner_diameter__mm`,
 1 AS `fe_bottom_id_tubing_out_color_code`,
 1 AS `fe_bottom_id_tubing_out_manufacturer`,
 1 AS `fe_bottom_id_tubing_out_model`,
 1 AS `fe_bottom_pump_rate_out__rpm`,
 1 AS `fe_bottom_flow_rate_real__mul_min`,
 1 AS `fe_bottom_name_electrolyte`,
 1 AS `fe_bottom_c_electrolyte__mol_L`,
 1 AS `fe_bottom_T_electrolyte__degC`,
 1 AS `fg_top_Arring_name_gas`,
 1 AS `fg_top_Arring_flow_rate__mL_min`,
 1 AS `fg_top_purgevial_name_gas`,
 1 AS `fg_top_purgevial_flow_rate__mL_min`,
 1 AS `fg_top_main_name_gas`,
 1 AS `fg_top_main_flow_rate__mL_min`,
 1 AS `fg_bottom_Arring_name_gas`,
 1 AS `fg_bottom_Arring_flow_rate__mL_min`,
 1 AS `fg_bottom_purgevial_name_gas`,
 1 AS `fg_bottom_purgevial_flow_rate__mL_min`,
 1 AS `fg_bottom_main_name_gas`,
 1 AS `fg_bottom_main_flow_rate__mL_min`*/;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `exp_ec_geis`
--

DROP TABLE IF EXISTS `exp_ec_geis`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `exp_ec_geis` (
  `id_exp_sfc` int NOT NULL COMMENT 'connects technique (GEIS) specific parameters to experiment parameters (exp_ec)',
  `name_technique` varchar(15) NOT NULL DEFAULT 'exp_ec_geis' COMMENT 'name of the technique - required to foreign key on exp_ec',
  `f_initial__Hz` float NOT NULL COMMENT 'initial frequency of the EIS measurement (usually higher frequency)',
  `f_final__Hz` float NOT NULL COMMENT 'final frequency of the EIS measurement (usually lower frequency)',
  `I_dc__A` float NOT NULL COMMENT 'offset DC current at which the EIS measurement should be performed. Actual measured current can be found in data_eis.',
  `I_amplitude__A` float NOT NULL COMMENT 'root mean square (RMS) of the current amplitude of the EIS measurement. The amplitude can be calculated by: amplitude = squareroot(2)*RMS.',
  `R_initialguess__ohm` float NOT NULL COMMENT 'inital guess for the uncompensated resistance',
  `points_per_decade` int NOT NULL COMMENT 'number of measurement points per frequency decade',
  PRIMARY KEY (`id_exp_sfc`,`name_technique`),
  KEY `FK_exp_ec_geis_name_technique_idx` (`name_technique`),
  CONSTRAINT `FK_exp_ec_geis` FOREIGN KEY (`id_exp_sfc`, `name_technique`) REFERENCES `exp_ec` (`id_exp_sfc`, `name_technique`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `FK_is_exp_ec_geis_name_technique` FOREIGN KEY (`name_technique`) REFERENCES `is_exp_ec_geis` (`name_technique`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='technique specific parameters for galvanostatic electrochemical impedance spectroscopy (GEIS)';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `exp_ec_ghold`
--

DROP TABLE IF EXISTS `exp_ec_ghold`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `exp_ec_ghold` (
  `id_exp_sfc` int NOT NULL COMMENT 'connects technique (ghold) specific parameters to experiment parameters (exp_ec)',
  `name_technique` varchar(15) NOT NULL DEFAULT 'exp_ec_ghold' COMMENT 'name of the technique - required to foreign key on exp_ec',
  `I_hold__A` float NOT NULL COMMENT 'current value which should be statically hold by potentiostat',
  `t_hold__s` float NOT NULL COMMENT 'duration of the current hold',
  `t_samplerate__s` float NOT NULL COMMENT 'time distance between acquisition of two data points',
  PRIMARY KEY (`id_exp_sfc`,`name_technique`),
  KEY `FK_exp_ec_ghold_name_technique_idx` (`name_technique`),
  CONSTRAINT `FK_exp_ec_ghold` FOREIGN KEY (`id_exp_sfc`, `name_technique`) REFERENCES `exp_ec` (`id_exp_sfc`, `name_technique`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `FK_is_exp_ec_ghold_name_technique` FOREIGN KEY (`name_technique`) REFERENCES `is_exp_ec_ghold` (`name_technique`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='technique specific parameters for galvanostatic hold (GHOLD), also called one step chronopotentiometry';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `exp_ec_gpulse`
--

DROP TABLE IF EXISTS `exp_ec_gpulse`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `exp_ec_gpulse` (
  `id_exp_sfc` int NOT NULL COMMENT 'connects technique (CV) specific parameters to experiment parameters (exp_ec)',
  `name_technique` varchar(15) NOT NULL DEFAULT 'exp_ec_gpulse' COMMENT 'name of the technique - required to foreign key on exp_ec',
  `I_hold1__A` float NOT NULL COMMENT 'current of the first hold (upper or lower)',
  `I_hold2__A` float NOT NULL COMMENT 'current of the first hold (upper or lower)',
  `t_hold1__s` float NOT NULL COMMENT 'holding time at I_hold1',
  `t_hold2__s` float NOT NULL COMMENT 'holding time at I_hold2',
  `t_samplerate__s` float NOT NULL COMMENT 'time distance between acquisition of two data points',
  `cycles` int NOT NULL COMMENT 'number of cycles',
  PRIMARY KEY (`id_exp_sfc`,`name_technique`),
  UNIQUE KEY `id_exp_ec_UNIQUE` (`id_exp_sfc`),
  KEY `FK_exp_ec_gpulse_name_technique_idx` (`name_technique`),
  CONSTRAINT `FK_exp_ec_gpulse` FOREIGN KEY (`id_exp_sfc`, `name_technique`) REFERENCES `exp_ec` (`id_exp_sfc`, `name_technique`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `FK_is_exp_ec_gpulse_name_technique` FOREIGN KEY (`name_technique`) REFERENCES `is_exp_ec_gpulse` (`name_technique`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='technique specific parameters for galvanostatic Pulse technique';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `exp_ec_integration`
--

DROP TABLE IF EXISTS `exp_ec_integration`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `exp_ec_integration` (
  `id_exp_ec_dataset` int NOT NULL COMMENT 'an integration can be performed over multiple exp_ec, relation between id_exp_ec_integration and id_exp_ec is stored in exp_ec_integration_id',
  `name_analysis` varchar(45) NOT NULL COMMENT 'name of the performed analysis',
  `id_ana_integration` int DEFAULT NULL COMMENT 'charge from integrated current following trapezoidal rule using python module numpy',
  `name_reaction` varchar(45) NOT NULL DEFAULT 'OER' COMMENT 'name of the electrochemical reaction as defined in ec_reactions',
  `faradaic_efficiency__percent` float NOT NULL DEFAULT '100' COMMENT 'faradaic efficiency of the reaction',
  PRIMARY KEY (`id_exp_ec_dataset`,`name_analysis`),
  KEY `FK_exp_ec_integration_id_exp_integration_idx` (`id_ana_integration`),
  KEY `FK_exp_ec_integration_name_reaction_idx` (`name_reaction`),
  CONSTRAINT `FK_exp_ec_integration_id_ana_integration` FOREIGN KEY (`id_ana_integration`) REFERENCES `ana_integrations` (`id_ana_integration`),
  CONSTRAINT `FK_exp_ec_integration_id_exp_ec_dataset` FOREIGN KEY (`id_exp_ec_dataset`) REFERENCES `exp_ec_datasets` (`id_exp_ec_dataset`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `FK_exp_ec_integration_name_reaction` FOREIGN KEY (`name_reaction`) REFERENCES `ec_reactions` (`name_reaction`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='all information from integration of ec data integration';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Temporary view structure for view `exp_ec_integration_expanded`
--

DROP TABLE IF EXISTS `exp_ec_integration_expanded`;
/*!50001 DROP VIEW IF EXISTS `exp_ec_integration_expanded`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `exp_ec_integration_expanded` AS SELECT 
 1 AS `id_exp_ec_dataset`,
 1 AS `id_ana_integration_ec`,
 1 AS `name_reaction`,
 1 AS `name_analysis`,
 1 AS `faradaic_efficiency__percent`,
 1 AS `name_exp_ec_dataset`,
 1 AS `name_product_of_interest`,
 1 AS `number_electrons`,
 1 AS `id_data_integration_ec_baseline`,
 1 AS `id_data_integration_ec_begin`,
 1 AS `id_data_integration_ec_end`,
 1 AS `t_integration_ec_baseline__timestamp`,
 1 AS `t_integration_ec_begin__timestamp`,
 1 AS `t_integration_ec_end__timestamp`,
 1 AS `Q_integrated_simps__C`,
 1 AS `Q_integrated_trapz__C`,
 1 AS `I_offset__A`,
 1 AS `no_of_datapoints_av_ec`,
 1 AS `no_of_datapoints_rolling_ec`,
 1 AS `auto_integration_ec`,
 1 AS `id_exp_sfc_first`,
 1 AS `id_exp_sfc`,
 1 AS `name_user`,
 1 AS `name_setup_sfc`,
 1 AS `name_setup_sfc_alias`,
 1 AS `name_setup_sfc_feature`,
 1 AS `name_setup_sfc_type`,
 1 AS `t_start__timestamp`,
 1 AS `t_end__timestamp`,
 1 AS `rawdata_path`,
 1 AS `rawdata_computer`,
 1 AS `id_ML`,
 1 AS `id_ML_technique`,
 1 AS `id_sample`,
 1 AS `id_spot`,
 1 AS `force__N`,
 1 AS `T_stage__degC`,
 1 AS `interrupted`,
 1 AS `labview_sfc_version`,
 1 AS `db_version`,
 1 AS `comment`,
 1 AS `ec_name_technique`,
 1 AS `ec_R_u__ohm`,
 1 AS `ec_iR_corr_in_situ__percent`,
 1 AS `ec_R_u_determining_exp_ec`,
 1 AS `ec_E_RE__VvsRHE`,
 1 AS `ec_name_RE`,
 1 AS `ec_name_RE_material`,
 1 AS `ec_name_RE_manufacturer`,
 1 AS `ec_name_RE_model`,
 1 AS `ec_name_CE`,
 1 AS `ec_name_CE_material`,
 1 AS `ec_name_CE_manufacturer`,
 1 AS `ec_name_CE_model`,
 1 AS `ec_name_device`,
 1 AS `ec_id_control_mode`,
 1 AS `ec_id_ie_range`,
 1 AS `ec_id_vch_range`,
 1 AS `ec_id_ich_range`,
 1 AS `ec_id_vch_filter`,
 1 AS `ec_id_ich_filter`,
 1 AS `ec_id_ca_speed`,
 1 AS `ec_id_ie_stability`,
 1 AS `ec_id_sampling_mode`,
 1 AS `ec_ie_range_auto`,
 1 AS `ec_vch_range_auto`,
 1 AS `ec_ich_range_auto`,
 1 AS `samples_id_sample`,
 1 AS `samples_name_sample`,
 1 AS `samples_name_user`,
 1 AS `samples_t_manufactured__timestamp`,
 1 AS `samples_comment`,
 1 AS `samples_total_loading__mg_cm2`,
 1 AS `spots_id_spot`,
 1 AS `spots_spot_size__mm2`,
 1 AS `spots_pos_x__mm`,
 1 AS `spots_pos_y__mm`,
 1 AS `spots_comment`,
 1 AS `spots_total_loading__mg_cm2`,
 1 AS `cv_E_initial__VvsRE`,
 1 AS `cv_E_apex1__VvsRE`,
 1 AS `cv_E_apex2__VvsRE`,
 1 AS `cv_E_final__VvsRE`,
 1 AS `cv_scanrate__mV_s`,
 1 AS `cv_stepsize__mV`,
 1 AS `cv_cycles`,
 1 AS `geis_f_initial__Hz`,
 1 AS `geis_f_final__Hz`,
 1 AS `geis_I_dc__A`,
 1 AS `geis_I_amplitude__A`,
 1 AS `geis_R_initialguess__ohm`,
 1 AS `geis_points_per_decade`,
 1 AS `ghold_I_hold__A`,
 1 AS `ghold_t_hold__s`,
 1 AS `ghold_t_samplerate__s`,
 1 AS `peis_f_initial__Hz`,
 1 AS `peis_f_final__Hz`,
 1 AS `peis_E_dc__VvsRE`,
 1 AS `peis_E_amplitude__VvsRE`,
 1 AS `peis_R_initialguess__ohm`,
 1 AS `peis_points_per_decade`,
 1 AS `phold_E_hold__VvsRE`,
 1 AS `phold_t_hold__s`,
 1 AS `phold_t_samplerate__s`,
 1 AS `ppulse_E_hold1__VvsRE`,
 1 AS `ppulse_E_hold2__VvsRE`,
 1 AS `ppulse_t_hold1__s`,
 1 AS `ppulse_t_hold2__s`,
 1 AS `ppulse_t_samplerate__s`,
 1 AS `ppulse_cycles`,
 1 AS `gpulse_I_hold1__A`,
 1 AS `gpulse_I_hold2__A`,
 1 AS `gpulse_t_hold1__s`,
 1 AS `gpulse_t_hold2__s`,
 1 AS `gpulse_t_samplerate__s`,
 1 AS `gpulse_cycles`,
 1 AS `ramp_E_initial__VvsRE`,
 1 AS `ramp_E_final__VvsRE`,
 1 AS `ramp_scanrate__mV_s`,
 1 AS `ramp_stepsize__mV`,
 1 AS `ramp_cycles`,
 1 AS `fc_top_name_flow_cell`,
 1 AS `fc_top_name_flow_cell_name_user`,
 1 AS `fc_top_name_flow_cell_material`,
 1 AS `fc_top_name_flow_cell_A_opening_ideal__mm2`,
 1 AS `fc_top_name_flow_cell_A_opening_real__mm2`,
 1 AS `fc_top_name_flow_cell_manufacture_date`,
 1 AS `fc_top_name_flow_cell_CAD_file`,
 1 AS `fc_top_name_flow_cell_comment`,
 1 AS `fc_top_id_sealing`,
 1 AS `fc_top_id_sealing_name_user`,
 1 AS `fc_top_id_sealing_material`,
 1 AS `fc_top_id_sealing_A_sealing__mm2`,
 1 AS `fc_top_id_sealing_A_opening__mm2`,
 1 AS `fc_top_id_sealing_thickness__mm`,
 1 AS `fc_top_id_sealing_shaping_method`,
 1 AS `fc_top_id_sealing_comment`,
 1 AS `fc_top_id_PTL`,
 1 AS `fc_top_id_PTL_name_user`,
 1 AS `fc_top_id_PTL_material`,
 1 AS `fc_top_id_PTL_thickness__mm`,
 1 AS `fc_top_id_PTL_manufacturer`,
 1 AS `fc_top_id_PTL_A_PTL__mm2`,
 1 AS `fc_top_id_PTL_shaping_method`,
 1 AS `fc_top_id_PTL_comment`,
 1 AS `fc_bottom_name_flow_cell`,
 1 AS `fc_bottom_name_flow_cell_name_user`,
 1 AS `fc_bottom_name_flow_cell_material`,
 1 AS `fc_bottom_name_flow_cell_A_opening_ideal__mm2`,
 1 AS `fc_bottom_name_flow_cell_A_opening_real__mm2`,
 1 AS `fc_bottom_name_flow_cell_manufacture_date`,
 1 AS `fc_bottom_name_flow_cell_CAD_file`,
 1 AS `fc_bottom_name_flow_cell_comment`,
 1 AS `fc_bottom_id_sealing`,
 1 AS `fc_bottom_id_sealing_name_user`,
 1 AS `fc_bottom_id_sealing_material`,
 1 AS `fc_bottom_id_sealing_A_sealing__mm2`,
 1 AS `fc_bottom_id_sealing_A_opening__mm2`,
 1 AS `fc_bottom_id_sealing_thickness__mm`,
 1 AS `fc_bottom_id_sealing_shaping_method`,
 1 AS `fc_bottom_id_sealing_comment`,
 1 AS `fc_bottom_id_PTL`,
 1 AS `fc_bottom_id_PTL_name_user`,
 1 AS `fc_bottom_id_PTL_material`,
 1 AS `fc_bottom_id_PTL_thickness__mm`,
 1 AS `fc_bottom_id_PTL_manufacturer`,
 1 AS `fc_bottom_id_PTL_A_PTL__mm2`,
 1 AS `fc_bottom_id_PTL_shaping_method`,
 1 AS `fc_bottom_id_PTL_comment`,
 1 AS `fe_top_id_pump_in`,
 1 AS `fe_top_id_pump_in_manufacturer`,
 1 AS `fe_top_id_pump_in_model`,
 1 AS `fe_top_id_pump_in_device`,
 1 AS `fe_top_id_tubing_in`,
 1 AS `fe_top_id_tubing_in_name_tubing`,
 1 AS `fe_top_id_tubing_in_inner_diameter__mm`,
 1 AS `fe_top_id_tubing_in_color_code`,
 1 AS `fe_top_id_tubing_in_manufacturer`,
 1 AS `fe_top_id_tubing_in_model`,
 1 AS `fe_top_pump_rate_in__rpm`,
 1 AS `fe_top_id_pump_out`,
 1 AS `fe_top_id_pump_out_manufacturer`,
 1 AS `fe_top_id_pump_out_model`,
 1 AS `fe_top_id_pump_out_device`,
 1 AS `fe_top_id_tubing_out`,
 1 AS `fe_top_id_tubing_out_name_tubing`,
 1 AS `fe_top_id_tubing_out_inner_diameter__mm`,
 1 AS `fe_top_id_tubing_out_color_code`,
 1 AS `fe_top_id_tubing_out_manufacturer`,
 1 AS `fe_top_id_tubing_out_model`,
 1 AS `fe_top_pump_rate_out__rpm`,
 1 AS `fe_top_flow_rate_real__mul_min`,
 1 AS `fe_top_name_electrolyte`,
 1 AS `fe_top_c_electrolyte__mol_L`,
 1 AS `fe_top_T_electrolyte__degC`,
 1 AS `fe_bottom_id_pump_in`,
 1 AS `fe_bottom_id_pump_in_manufacturer`,
 1 AS `fe_bottom_id_pump_in_model`,
 1 AS `fe_bottom_id_pump_in_device`,
 1 AS `fe_bottom_id_tubing_in`,
 1 AS `fe_bottom_id_tubing_in_name_tubing`,
 1 AS `fe_bottom_id_tubing_in_inner_diameter__mm`,
 1 AS `fe_bottom_id_tubing_in_color_code`,
 1 AS `fe_bottom_id_tubing_in_manufacturer`,
 1 AS `fe_bottom_id_tubing_in_model`,
 1 AS `fe_bottom_pump_rate_in__rpm`,
 1 AS `fe_bottom_id_pump_out`,
 1 AS `fe_bottom_id_pump_out_manufacturer`,
 1 AS `fe_bottom_id_pump_out_model`,
 1 AS `fe_bottom_id_pump_out_device`,
 1 AS `fe_bottom_id_tubing_out`,
 1 AS `fe_bottom_id_tubing_out_name_tubing`,
 1 AS `fe_bottom_id_tubing_out_inner_diameter__mm`,
 1 AS `fe_bottom_id_tubing_out_color_code`,
 1 AS `fe_bottom_id_tubing_out_manufacturer`,
 1 AS `fe_bottom_id_tubing_out_model`,
 1 AS `fe_bottom_pump_rate_out__rpm`,
 1 AS `fe_bottom_flow_rate_real__mul_min`,
 1 AS `fe_bottom_name_electrolyte`,
 1 AS `fe_bottom_c_electrolyte__mol_L`,
 1 AS `fe_bottom_T_electrolyte__degC`,
 1 AS `fg_top_Arring_name_gas`,
 1 AS `fg_top_Arring_flow_rate__mL_min`,
 1 AS `fg_top_purgevial_name_gas`,
 1 AS `fg_top_purgevial_flow_rate__mL_min`,
 1 AS `fg_top_main_name_gas`,
 1 AS `fg_top_main_flow_rate__mL_min`,
 1 AS `fg_bottom_Arring_name_gas`,
 1 AS `fg_bottom_Arring_flow_rate__mL_min`,
 1 AS `fg_bottom_purgevial_name_gas`,
 1 AS `fg_bottom_purgevial_flow_rate__mL_min`,
 1 AS `fg_bottom_main_name_gas`,
 1 AS `fg_bottom_main_flow_rate__mL_min`,
 1 AS `n_product_of_interest_simps__mol`,
 1 AS `n_product_of_interest_trapz__mol`*/;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `exp_ec_peis`
--

DROP TABLE IF EXISTS `exp_ec_peis`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `exp_ec_peis` (
  `id_exp_sfc` int NOT NULL COMMENT 'connects technique (PEIS) specific parameters to experiment parameters (exp_ec)',
  `name_technique` varchar(15) NOT NULL DEFAULT 'exp_ec_peis' COMMENT 'name of the technique - required to foreign key on exp_ec',
  `f_initial__Hz` float NOT NULL COMMENT 'initial frequency of the EIS measurement (usually higher frequency)',
  `f_final__Hz` float NOT NULL COMMENT 'final frequency of the EIS measurement (usually lower frequency)',
  `E_dc__VvsRE` float NOT NULL COMMENT 'offset DC potential at which the EIS measurement should be performed. Actual measured potetnial can be found in data_eis.',
  `E_amplitude__VvsRE` float NOT NULL COMMENT 'root mean square (RMS) of the potential amplitude of the EIS measurement. The amplitude can be calculated by: amplitude = squareroot(2)*RMS.',
  `R_initialguess__ohm` float NOT NULL COMMENT 'inital guess for the uncompensated resistance',
  `points_per_decade` int NOT NULL COMMENT 'number of measurement points per frequency decade',
  PRIMARY KEY (`id_exp_sfc`,`name_technique`),
  KEY `FK_exp_ec_peis_name_technique_idx` (`name_technique`),
  CONSTRAINT `FK_exp_ec_peis` FOREIGN KEY (`id_exp_sfc`, `name_technique`) REFERENCES `exp_ec` (`id_exp_sfc`, `name_technique`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `FK_is_exp_ec_peis_name_technique` FOREIGN KEY (`name_technique`) REFERENCES `is_exp_ec_peis` (`name_technique`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='technique specific parameters for potentiostatic electrochemical impedance spectroscopy (PEIS)';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `exp_ec_phold`
--

DROP TABLE IF EXISTS `exp_ec_phold`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `exp_ec_phold` (
  `id_exp_sfc` int NOT NULL COMMENT 'connects technique (phold) specific parameters to experiment parameters (exp_ec)',
  `name_technique` varchar(15) NOT NULL DEFAULT 'exp_ec_phold' COMMENT 'name of the technique - required to foreign key on exp_ec',
  `E_hold__VvsRE` float NOT NULL COMMENT 'potential value against refernce electrode which should be statically hold by potentiostat',
  `t_hold__s` float NOT NULL COMMENT 'duration of the potential hold',
  `t_samplerate__s` float NOT NULL COMMENT 'time distance between acquisition of two data points',
  PRIMARY KEY (`id_exp_sfc`,`name_technique`),
  KEY `FK_exp_ec_phold_name_technique_idx` (`name_technique`),
  CONSTRAINT `FK_exp_ec_phold` FOREIGN KEY (`id_exp_sfc`, `name_technique`) REFERENCES `exp_ec` (`id_exp_sfc`, `name_technique`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `FK_is_exp_ec_phold_name_technique` FOREIGN KEY (`name_technique`) REFERENCES `is_exp_ec_phold` (`name_technique`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='technique specific parameters for galvanostatic hold (PHOLD), also called one step chronoamperometry';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `exp_ec_polcurve`
--

DROP TABLE IF EXISTS `exp_ec_polcurve`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `exp_ec_polcurve` (
  `id_exp_ec_polcurve` int NOT NULL AUTO_INCREMENT COMMENT 'index of polarization experiments',
  `number_datapoints_in_tail` int NOT NULL COMMENT 'number of datapoints used at the end of the ghold to derive averaged current and potential',
  `changed_exp_parameters` varchar(254) DEFAULT NULL COMMENT 'list of columns which were changed during the course of the experiment. This should usually be empty.',
  `t_inserted_data__timestamp` datetime DEFAULT NULL COMMENT 'timestamp of processed data insertion',
  `file_path_processing_plot` varchar(254) DEFAULT NULL COMMENT 'file path to the processed data plot',
  `chosen_j_geo_col` varchar(45) DEFAULT NULL COMMENT 'chosen geometric current column used to display and fit the data',
  `tafel_fit_left_limit__j_geo` float DEFAULT NULL COMMENT 'lower (lower) limit of the tafel fit in unit of the chosen geometric current column',
  `tafel_fit_right_limit__j_geo` float DEFAULT NULL COMMENT 'right (upper) limit of the tafel fit',
  `tafel_fit_m__V_dec` float DEFAULT NULL COMMENT 'tafel slope',
  `tafel_fit_m_sd__V_dec` float DEFAULT NULL COMMENT 'stadard deviation of tafel slope',
  `tafel_fit_b__VvsRHE` float DEFAULT NULL COMMENT 'tafel fit y-axis intercept',
  `tafel_fit_b_sd__VsRHE` float DEFAULT NULL COMMENT 'standard deviation of the tafel plot y-axis intercept',
  `tafel_fit_ResVar` float DEFAULT NULL COMMENT 'residual variance of the fitting method',
  `tafel_fit_method` varchar(45) DEFAULT NULL COMMENT 'applied fitting method',
  PRIMARY KEY (`id_exp_ec_polcurve`)
) ENGINE=InnoDB AUTO_INCREMENT=80 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='experimental information for polarization curve experiments. (Combination of geis and ghold)';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Temporary view structure for view `exp_ec_polcurve_expanded`
--

DROP TABLE IF EXISTS `exp_ec_polcurve_expanded`;
/*!50001 DROP VIEW IF EXISTS `exp_ec_polcurve_expanded`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `exp_ec_polcurve_expanded` AS SELECT 
 1 AS `id_exp_ec_polcurve`,
 1 AS `number_datapoints_in_tail`,
 1 AS `changed_exp_parameters`,
 1 AS `t_inserted_data__timestamp`,
 1 AS `file_path_processing_plot`,
 1 AS `id_exp_sfc_ghold_first`,
 1 AS `id_exp_sfc_geis_first`,
 1 AS `id_exp_sfc`,
 1 AS `name_user`,
 1 AS `name_setup_sfc`,
 1 AS `name_setup_sfc_alias`,
 1 AS `name_setup_sfc_feature`,
 1 AS `name_setup_sfc_type`,
 1 AS `t_start__timestamp`,
 1 AS `rawdata_path`,
 1 AS `rawdata_computer`,
 1 AS `id_ML`,
 1 AS `id_ML_technique`,
 1 AS `id_sample`,
 1 AS `id_spot`,
 1 AS `force__N`,
 1 AS `T_stage__degC`,
 1 AS `interrupted`,
 1 AS `labview_sfc_version`,
 1 AS `db_version`,
 1 AS `comment`,
 1 AS `t_end__timestamp`,
 1 AS `ec_name_technique`,
 1 AS `ec_R_u__ohm`,
 1 AS `ec_iR_corr_in_situ__percent`,
 1 AS `ec_R_u_determining_exp_ec`,
 1 AS `ec_E_RE__VvsRHE`,
 1 AS `ec_name_RE`,
 1 AS `ec_name_RE_material`,
 1 AS `ec_name_RE_manufacturer`,
 1 AS `ec_name_RE_model`,
 1 AS `ec_name_CE`,
 1 AS `ec_name_CE_material`,
 1 AS `ec_name_CE_manufacturer`,
 1 AS `ec_name_CE_model`,
 1 AS `ec_name_device`,
 1 AS `ec_id_control_mode`,
 1 AS `ec_id_ie_range`,
 1 AS `ec_id_vch_range`,
 1 AS `ec_id_ich_range`,
 1 AS `ec_id_vch_filter`,
 1 AS `ec_id_ich_filter`,
 1 AS `ec_id_ca_speed`,
 1 AS `ec_id_ie_stability`,
 1 AS `ec_id_sampling_mode`,
 1 AS `ec_ie_range_auto`,
 1 AS `ec_vch_range_auto`,
 1 AS `ec_ich_range_auto`,
 1 AS `samples_id_sample`,
 1 AS `samples_name_sample`,
 1 AS `samples_name_user`,
 1 AS `samples_t_manufactured__timestamp`,
 1 AS `samples_comment`,
 1 AS `samples_total_loading__mg_cm2`,
 1 AS `spots_id_spot`,
 1 AS `spots_spot_size__mm2`,
 1 AS `spots_pos_x__mm`,
 1 AS `spots_pos_y__mm`,
 1 AS `spots_comment`,
 1 AS `spots_total_loading__mg_cm2`,
 1 AS `cv_E_initial__VvsRE`,
 1 AS `cv_E_apex1__VvsRE`,
 1 AS `cv_E_apex2__VvsRE`,
 1 AS `cv_E_final__VvsRE`,
 1 AS `cv_scanrate__mV_s`,
 1 AS `cv_stepsize__mV`,
 1 AS `cv_cycles`,
 1 AS `ghold_I_hold__A`,
 1 AS `ghold_t_hold__s`,
 1 AS `ghold_t_samplerate__s`,
 1 AS `peis_f_initial__Hz`,
 1 AS `peis_f_final__Hz`,
 1 AS `peis_E_dc__VvsRE`,
 1 AS `peis_E_amplitude__VvsRE`,
 1 AS `peis_R_initialguess__ohm`,
 1 AS `peis_points_per_decade`,
 1 AS `phold_E_hold__VvsRE`,
 1 AS `phold_t_hold__s`,
 1 AS `phold_t_samplerate__s`,
 1 AS `ppulse_E_hold1__VvsRE`,
 1 AS `ppulse_E_hold2__VvsRE`,
 1 AS `ppulse_t_hold1__s`,
 1 AS `ppulse_t_hold2__s`,
 1 AS `ppulse_t_samplerate__s`,
 1 AS `ppulse_cycles`,
 1 AS `gpulse_I_hold1__A`,
 1 AS `gpulse_I_hold2__A`,
 1 AS `gpulse_t_hold1__s`,
 1 AS `gpulse_t_hold2__s`,
 1 AS `gpulse_t_samplerate__s`,
 1 AS `gpulse_cycles`,
 1 AS `ramp_E_initial__VvsRE`,
 1 AS `ramp_E_final__VvsRE`,
 1 AS `ramp_scanrate__mV_s`,
 1 AS `ramp_stepsize__mV`,
 1 AS `ramp_cycles`,
 1 AS `fc_top_name_flow_cell`,
 1 AS `fc_top_name_flow_cell_name_user`,
 1 AS `fc_top_name_flow_cell_material`,
 1 AS `fc_top_name_flow_cell_A_opening_ideal__mm2`,
 1 AS `fc_top_name_flow_cell_A_opening_real__mm2`,
 1 AS `fc_top_name_flow_cell_manufacture_date`,
 1 AS `fc_top_name_flow_cell_CAD_file`,
 1 AS `fc_top_name_flow_cell_comment`,
 1 AS `fc_top_id_sealing`,
 1 AS `fc_top_id_sealing_name_user`,
 1 AS `fc_top_id_sealing_material`,
 1 AS `fc_top_id_sealing_A_sealing__mm2`,
 1 AS `fc_top_id_sealing_A_opening__mm2`,
 1 AS `fc_top_id_sealing_thickness__mm`,
 1 AS `fc_top_id_sealing_shaping_method`,
 1 AS `fc_top_id_sealing_comment`,
 1 AS `fc_top_id_PTL`,
 1 AS `fc_top_id_PTL_name_user`,
 1 AS `fc_top_id_PTL_material`,
 1 AS `fc_top_id_PTL_thickness__mm`,
 1 AS `fc_top_id_PTL_manufacturer`,
 1 AS `fc_top_id_PTL_A_PTL__mm2`,
 1 AS `fc_top_id_PTL_shaping_method`,
 1 AS `fc_top_id_PTL_comment`,
 1 AS `fc_bottom_name_flow_cell`,
 1 AS `fc_bottom_name_flow_cell_name_user`,
 1 AS `fc_bottom_name_flow_cell_material`,
 1 AS `fc_bottom_name_flow_cell_A_opening_ideal__mm2`,
 1 AS `fc_bottom_name_flow_cell_A_opening_real__mm2`,
 1 AS `fc_bottom_name_flow_cell_manufacture_date`,
 1 AS `fc_bottom_name_flow_cell_CAD_file`,
 1 AS `fc_bottom_name_flow_cell_comment`,
 1 AS `fc_bottom_id_sealing`,
 1 AS `fc_bottom_id_sealing_name_user`,
 1 AS `fc_bottom_id_sealing_material`,
 1 AS `fc_bottom_id_sealing_A_sealing__mm2`,
 1 AS `fc_bottom_id_sealing_A_opening__mm2`,
 1 AS `fc_bottom_id_sealing_thickness__mm`,
 1 AS `fc_bottom_id_sealing_shaping_method`,
 1 AS `fc_bottom_id_sealing_comment`,
 1 AS `fc_bottom_id_PTL`,
 1 AS `fc_bottom_id_PTL_name_user`,
 1 AS `fc_bottom_id_PTL_material`,
 1 AS `fc_bottom_id_PTL_thickness__mm`,
 1 AS `fc_bottom_id_PTL_manufacturer`,
 1 AS `fc_bottom_id_PTL_A_PTL__mm2`,
 1 AS `fc_bottom_id_PTL_shaping_method`,
 1 AS `fc_bottom_id_PTL_comment`,
 1 AS `fe_top_id_pump_in`,
 1 AS `fe_top_id_pump_in_manufacturer`,
 1 AS `fe_top_id_pump_in_model`,
 1 AS `fe_top_id_pump_in_device`,
 1 AS `fe_top_id_tubing_in`,
 1 AS `fe_top_id_tubing_in_name_tubing`,
 1 AS `fe_top_id_tubing_in_inner_diameter__mm`,
 1 AS `fe_top_id_tubing_in_color_code`,
 1 AS `fe_top_id_tubing_in_manufacturer`,
 1 AS `fe_top_id_tubing_in_model`,
 1 AS `fe_top_pump_rate_in__rpm`,
 1 AS `fe_top_id_pump_out`,
 1 AS `fe_top_id_pump_out_manufacturer`,
 1 AS `fe_top_id_pump_out_model`,
 1 AS `fe_top_id_pump_out_device`,
 1 AS `fe_top_id_tubing_out`,
 1 AS `fe_top_id_tubing_out_name_tubing`,
 1 AS `fe_top_id_tubing_out_inner_diameter__mm`,
 1 AS `fe_top_id_tubing_out_color_code`,
 1 AS `fe_top_id_tubing_out_manufacturer`,
 1 AS `fe_top_id_tubing_out_model`,
 1 AS `fe_top_pump_rate_out__rpm`,
 1 AS `fe_top_flow_rate_real__mul_min`,
 1 AS `fe_top_name_electrolyte`,
 1 AS `fe_top_c_electrolyte__mol_L`,
 1 AS `fe_top_T_electrolyte__degC`,
 1 AS `fe_bottom_id_pump_in`,
 1 AS `fe_bottom_id_pump_in_manufacturer`,
 1 AS `fe_bottom_id_pump_in_model`,
 1 AS `fe_bottom_id_pump_in_device`,
 1 AS `fe_bottom_id_tubing_in`,
 1 AS `fe_bottom_id_tubing_in_name_tubing`,
 1 AS `fe_bottom_id_tubing_in_inner_diameter__mm`,
 1 AS `fe_bottom_id_tubing_in_color_code`,
 1 AS `fe_bottom_id_tubing_in_manufacturer`,
 1 AS `fe_bottom_id_tubing_in_model`,
 1 AS `fe_bottom_pump_rate_in__rpm`,
 1 AS `fe_bottom_id_pump_out`,
 1 AS `fe_bottom_id_pump_out_manufacturer`,
 1 AS `fe_bottom_id_pump_out_model`,
 1 AS `fe_bottom_id_pump_out_device`,
 1 AS `fe_bottom_id_tubing_out`,
 1 AS `fe_bottom_id_tubing_out_name_tubing`,
 1 AS `fe_bottom_id_tubing_out_inner_diameter__mm`,
 1 AS `fe_bottom_id_tubing_out_color_code`,
 1 AS `fe_bottom_id_tubing_out_manufacturer`,
 1 AS `fe_bottom_id_tubing_out_model`,
 1 AS `fe_bottom_pump_rate_out__rpm`,
 1 AS `fe_bottom_flow_rate_real__mul_min`,
 1 AS `fe_bottom_name_electrolyte`,
 1 AS `fe_bottom_c_electrolyte__mol_L`,
 1 AS `fe_bottom_T_electrolyte__degC`,
 1 AS `fg_top_Arring_name_gas`,
 1 AS `fg_top_Arring_flow_rate__mL_min`,
 1 AS `fg_top_purgevial_name_gas`,
 1 AS `fg_top_purgevial_flow_rate__mL_min`,
 1 AS `fg_top_main_name_gas`,
 1 AS `fg_top_main_flow_rate__mL_min`,
 1 AS `fg_bottom_Arring_name_gas`,
 1 AS `fg_bottom_Arring_flow_rate__mL_min`,
 1 AS `fg_bottom_purgevial_name_gas`,
 1 AS `fg_bottom_purgevial_flow_rate__mL_min`,
 1 AS `fg_bottom_main_name_gas`,
 1 AS `fg_bottom_main_flow_rate__mL_min`,
 1 AS `id_exp_sfc_geis`,
 1 AS `geis_f_initial__Hz`,
 1 AS `geis_f_final__Hz`,
 1 AS `geis_I_dc__A`,
 1 AS `geis_I_amplitude__A`,
 1 AS `geis_R_initialguess__ohm`,
 1 AS `geis_points_per_decade`*/;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `exp_ec_ppulse`
--

DROP TABLE IF EXISTS `exp_ec_ppulse`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `exp_ec_ppulse` (
  `id_exp_sfc` int NOT NULL COMMENT 'connects technique (CV) specific parameters to experiment parameters (exp_ec)',
  `name_technique` varchar(15) NOT NULL DEFAULT 'exp_ec_ppulse' COMMENT 'name of the technique - required to foreign key on exp_ec',
  `E_hold1__VvsRE` float NOT NULL COMMENT 'potential of the first hold (upper or lower) against reference electrode potential',
  `E_hold2__VvsRE` float NOT NULL COMMENT 'potential of the first hold (upper or lower) against reference electrode potential',
  `t_hold1__s` float NOT NULL COMMENT 'holding time at E_hold1',
  `t_hold2__s` float NOT NULL COMMENT 'holding time at E_hold2',
  `t_samplerate__s` float NOT NULL COMMENT 'time distance between acquisition of two data points',
  `cycles` int NOT NULL COMMENT 'number of cycles',
  PRIMARY KEY (`id_exp_sfc`,`name_technique`),
  UNIQUE KEY `id_exp_ec_UNIQUE` (`id_exp_sfc`),
  KEY `FK_exp_ec_ppulse_name_technique_idx` (`name_technique`),
  CONSTRAINT `FK_exp_ec_ppulse` FOREIGN KEY (`id_exp_sfc`, `name_technique`) REFERENCES `exp_ec` (`id_exp_sfc`, `name_technique`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `FK_is_exp_ec_ppulse_name_technique` FOREIGN KEY (`name_technique`) REFERENCES `is_exp_ec_ppulse` (`name_technique`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='technique specific parameters for potentiostatic Pulse technique';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `exp_ec_ramp`
--

DROP TABLE IF EXISTS `exp_ec_ramp`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `exp_ec_ramp` (
  `id_exp_sfc` int NOT NULL COMMENT 'connects technique (ramp) specific parameters to experiment parameters (exp_ec)',
  `name_technique` varchar(15) NOT NULL DEFAULT 'exp_ec_ramp' COMMENT 'name of the technique - required to foreign key on exp_ec',
  `E_initial__VvsRE` float NOT NULL COMMENT 'inital potential of the LSV against reference electrode potential',
  `E_final__VvsRE` float NOT NULL COMMENT 'final potential of the LSV against reference electrode potential',
  `scanrate__mV_s` float NOT NULL COMMENT 'potential scanrate of the CV experiemnt in milli Volt per second',
  `stepsize__mV` float NOT NULL COMMENT 'potential stepsize of the LSV',
  `cycles` int NOT NULL COMMENT 'number of cycles',
  PRIMARY KEY (`id_exp_sfc`,`name_technique`),
  KEY `FK_exp_ec_ramp_name_technique_idx` (`name_technique`),
  CONSTRAINT `FK_exp_ec_ramp` FOREIGN KEY (`id_exp_sfc`, `name_technique`) REFERENCES `exp_ec` (`id_exp_sfc`, `name_technique`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `FK_is_exp_ec_ramp_name_technique` FOREIGN KEY (`name_technique`) REFERENCES `is_exp_ec_ramp` (`name_technique`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='technique specific parameters for a potential ramp or linear sweep voltammetry (LSV)';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `exp_ec_techniques`
--

DROP TABLE IF EXISTS `exp_ec_techniques`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `exp_ec_techniques` (
  `name_technique` varchar(15) NOT NULL COMMENT 'name of the technique - required to put an ENUM on name_technique column in exp_ec, while being able to foreign key from technique tables to exp_ec',
  PRIMARY KEY (`name_technique`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Stores implemented ec techniques, necessary to guarantee a correct storage of technique specific parameters. This is a so-called super/subtype construct.';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `exp_icpms`
--

DROP TABLE IF EXISTS `exp_icpms`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `exp_icpms` (
  `id_exp_icpms` int NOT NULL AUTO_INCREMENT COMMENT 'Database internal index of the icpms experiment, to relate experiment to other tables.',
  `name_sample` varchar(45) DEFAULT NULL COMMENT 'name of the sample as given in Agilent Masshunter Software. Inserted from BatchLog.csv',
  `name_user` varchar(40) NOT NULL COMMENT 'name of the experimentator',
  `name_setup_icpms` varchar(40) NOT NULL COMMENT 'name of the used icpms setup',
  `t_start__timestamp_icpms_pc` varchar(45) NOT NULL COMMENT 'starting timestamp according to  ICP-MS computer',
  `t_duration__s` float DEFAULT NULL COMMENT 'duration of the icp-ms experiment',
  `t_duration_planned__s` float DEFAULT NULL COMMENT 'planned duration of the icp-ms experiment as set in AgilentMasshunter Software',
  `type_experiment` enum('calibration','batch','sfc-icpms','sfc-batch') NOT NULL COMMENT 'type of the experiment: calibration = experiment to determine one point of the calibrationm curve with known concentration nof the analyt(s); batch = measuring analyte concentration of one batch sample; sfc-icpms = continuous icpms experiment recorded while connected to SFC; sfc-batch bacth sample collected on a sfc electrolyte flow measured separately;',
  `plasma_mode` varchar(45) DEFAULT NULL COMMENT 'Plasma mode of the device: Low Matrix, General Purpose or HMI',
  `tune_mode` varchar(45) DEFAULT NULL COMMENT 'tune mode of icpms plasma from Agilent device. Inserted from Method/AcqMethod.xml',
  `num_of_scans` int DEFAULT NULL COMMENT 'number of scans performed during the acquisition time. Inserted from "name_sample"AcqData/MSTS.xml',
  `id_exp_icpms_calibration_set` int NOT NULL COMMENT 'index of the related calibration set. For calibration experiments it will indicate to which calibration set it belong, for others it indicates which calibration set is intended to be used for purpose of correction.',
  `gas_dilution_factor` float DEFAULT NULL COMMENT 'Dilution of analyte liquid by gas inside ICP-MS device. Factor must be equal for calibration and experiment. For that case the factor will cancel out.',
  `name_gas_collision` varchar(45) DEFAULT NULL COMMENT 'name of the collision gas used in the ICP-MS device',
  `flow_rate_collision__mL_min` float DEFAULT NULL COMMENT 'flowrate of the collision gas',
  `name_gas_reaction` varchar(45) DEFAULT NULL COMMENT 'name of the gas for dynamic reaction cell (DRC), necessary for some elements to avoid formation of complexes with other other m/z ratios.',
  `flow_rate_reaction__mL_min` float DEFAULT NULL COMMENT 'flow rate of the reaction gas',
  `comment` text COMMENT 'user comment',
  `name_computer_inserted_data` varchar(45) NOT NULL COMMENT 'name of the computer on which the insertion script was performed',
  `file_path_rawdata` varchar(254) NOT NULL COMMENT 'file path of the rawdata on the computer "name_computer_inserted_data"',
  `t_inserted_data__timestamp` datetime NOT NULL COMMENT 'timestamp of the insertion routine',
  `file_name_rawdata` varchar(45) NOT NULL COMMENT 'name of the raw data file. Necessary to have UNIQUE constratint as long as the start time of measuring is not stored in the file.',
  `batch_name` varchar(254) DEFAULT NULL COMMENT 'name of the batch given by Agilent Software',
  PRIMARY KEY (`id_exp_icpms`),
  UNIQUE KEY `UNIQUE_exp_icpms_id_exp_icpms_type_experiment_id_calib_set` (`id_exp_icpms`,`type_experiment`,`id_exp_icpms_calibration_set`) COMMENT '''redundance for this table, but necessary to have id_exp_icpms+type_experiment+id_exp_icpms_calibration_set as FK in exp_icpms_analyte_internalstandard table''' /*!80000 INVISIBLE */,
  UNIQUE KEY `UNIQUE_exp_icpms_device_timestamp` (`t_start__timestamp_icpms_pc`,`name_setup_icpms`,`file_name_rawdata`) /*!80000 INVISIBLE */,
  KEY `FK_exp_icpms_name_user_idx` (`name_user`),
  KEY `FK_exp_icpms_name_setup_icpms_idx` (`name_setup_icpms`),
  KEY `FK_exp_icpms_name_gas_collision_idx` (`name_gas_collision`),
  KEY `FK_exp_icpms_name_gas_collision_idx1` (`name_gas_reaction`),
  KEY `FK_exp_icpms_id_calibration_set_idx` (`id_exp_icpms_calibration_set`),
  CONSTRAINT `FK_exp_icpms_id_calibration_set` FOREIGN KEY (`id_exp_icpms_calibration_set`) REFERENCES `exp_icpms_calibration_set` (`id_exp_icpms_calibration_set`),
  CONSTRAINT `FK_exp_icpms_name_gas_collision` FOREIGN KEY (`name_gas_collision`) REFERENCES `gases` (`name_gas`),
  CONSTRAINT `FK_exp_icpms_name_gas_reaction` FOREIGN KEY (`name_gas_reaction`) REFERENCES `gases` (`name_gas`),
  CONSTRAINT `FK_exp_icpms_name_setup_icpms` FOREIGN KEY (`name_setup_icpms`) REFERENCES `setups_icpms` (`name_setup_icpms`),
  CONSTRAINT `FK_exp_icpms_name_user` FOREIGN KEY (`name_user`) REFERENCES `users` (`name_user`) ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=532 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Table storing all ICPMS experiments including calibration, bulk and sfc-icpms experiments';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `exp_icpms_analyte_internalstandard`
--

DROP TABLE IF EXISTS `exp_icpms_analyte_internalstandard`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `exp_icpms_analyte_internalstandard` (
  `id_exp_icpms` int NOT NULL COMMENT 'Index of the icpms experiment',
  `name_isotope_analyte` varchar(45) NOT NULL COMMENT 'name of the analyte isotope',
  `name_isotope_internalstandard` varchar(45) NOT NULL COMMENT 'name of the internal standard isotope',
  `type_experiment` enum('calibration','batch','sfc-icpms','sfc-batch') NOT NULL COMMENT 'as defined in table exp_icpms. Copy is necessary here to internally check whether NULL on c_analyte__mol_L is allowed or not. (Value has to be given but only for calibration experiments)',
  `c_analyte__mug_L` float DEFAULT NULL COMMENT 'Analyte concentration in µg per Liter. Values given for calibration experiments. Others (sfc-icpms, batch) will get NULL',
  `c_internalstandard__mug_L` float NOT NULL COMMENT 'concentration of the internal standard in µg per Liter',
  `id_exp_icpms_calibration_set` int NOT NULL COMMENT 'as set in exp_icpms. Redundant copy here is necessary to constrain possible analyte internal standard pairs for a given calibration set in table exp_icpms_calibration_params',
  `t_integration_analyte__s` float DEFAULT NULL COMMENT 'integration time of the analyte isotope during one scan. Inserted from Method/AcqMethod.xml',
  `t_integration_internalstandard__s` float DEFAULT NULL COMMENT 'integration time of the internalstandard isotope during one scan. Inserted from Method/AcqMethod.xml',
  PRIMARY KEY (`id_exp_icpms`,`name_isotope_analyte`,`name_isotope_internalstandard`),
  KEY `FK_name_isotope_analyte_idx` (`name_isotope_analyte`) /*!80000 INVISIBLE */,
  KEY `FK_name_isotope_internalstandard_idx` (`name_isotope_internalstandard`),
  KEY `FK_exp_icpms_an_instd_id_exp_icpms_type_exp_calib_set_idx` (`id_exp_icpms`,`type_experiment`,`id_exp_icpms_calibration_set`),
  KEY `INDEX_id_calib_set_name_analyte_internalstandard` (`id_exp_icpms_calibration_set`,`name_isotope_analyte`,`name_isotope_internalstandard`) /*!80000 INVISIBLE */,
  KEY `INDEX_id_exp_icpms_analyte_internalstandard` (`id_exp_icpms`,`name_isotope_analyte`,`name_isotope_internalstandard`),
  CONSTRAINT `FK_exp_icpms_an_instd_id_exp_icpms_type_exp_calib_set` FOREIGN KEY (`id_exp_icpms`, `type_experiment`, `id_exp_icpms_calibration_set`) REFERENCES `exp_icpms` (`id_exp_icpms`, `type_experiment`, `id_exp_icpms_calibration_set`),
  CONSTRAINT `FK_name_isotope_analyte` FOREIGN KEY (`name_isotope_analyte`) REFERENCES `isotopes` (`name_isotope`),
  CONSTRAINT `FK_name_isotope_internalstandard` FOREIGN KEY (`name_isotope_internalstandard`) REFERENCES `isotopes` (`name_isotope`),
  CONSTRAINT `CHECK_exp_icpms_c_analyte__mug_L_optional_for_calibration` CHECK ((((`type_experiment` = _utf8mb4'calibration') and (`c_analyte__mug_L` is not null)) or (`type_experiment` = _utf8mb4'batch') or ((`type_experiment` <> _utf8mb4'calibration') and (`c_analyte__mug_L` is null))))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Relationship of analyte and internal standard in icp-ms experiment. Multiple relationships can be handled, also multiple analytes for one internal standard and vice versa. ';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Temporary view structure for view `exp_icpms_batch_expanded`
--

DROP TABLE IF EXISTS `exp_icpms_batch_expanded`;
/*!50001 DROP VIEW IF EXISTS `exp_icpms_batch_expanded`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `exp_icpms_batch_expanded` AS SELECT 
 1 AS `id_exp_icpms`,
 1 AS `name_isotope_analyte`,
 1 AS `name_isotope_internalstandard`,
 1 AS `name_sample`,
 1 AS `name_user`,
 1 AS `name_setup_icpms`,
 1 AS `t_start__timestamp_icpms_pc`,
 1 AS `t_duration__s`,
 1 AS `t_duration_planned__s`,
 1 AS `type_experiment`,
 1 AS `plasma_mode`,
 1 AS `tune_mode`,
 1 AS `num_of_scans`,
 1 AS `id_exp_icpms_calibration_set`,
 1 AS `gas_dilution_factor`,
 1 AS `name_gas_collision`,
 1 AS `flow_rate_collision__mL_min`,
 1 AS `name_gas_reaction`,
 1 AS `flow_rate_reaction__mL_min`,
 1 AS `comment`,
 1 AS `name_computer_inserted_data`,
 1 AS `file_path_rawdata`,
 1 AS `t_inserted_data__timestamp`,
 1 AS `file_name_rawdata`,
 1 AS `batch_name`,
 1 AS `c_analyte_0__mug_L`,
 1 AS `c_internalstandard__mug_L`,
 1 AS `t_integration_analyte__s`,
 1 AS `t_integration_internalstandard__s`,
 1 AS `calibration_slope__countratio_mug_L`,
 1 AS `delta_calibration_slope__countratio_mug_L`,
 1 AS `calibration_intercept__countratio`,
 1 AS `delta_calibration_intercept__countratio`,
 1 AS `Rsquared`,
 1 AS `calibration_method`,
 1 AS `file_path_calibration_plot`,
 1 AS `name_computer_inserted_calibration_data`,
 1 AS `t_inserted_calibration_data__timestamp`,
 1 AS `counts_analyte_mean`,
 1 AS `counts_analyte_std`,
 1 AS `counts_internalstandard_mean`,
 1 AS `counts_internalstandard_std`,
 1 AS `a_is__countratio`,
 1 AS `c_a__mug_L`*/;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `exp_icpms_calibration_params`
--

DROP TABLE IF EXISTS `exp_icpms_calibration_params`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `exp_icpms_calibration_params` (
  `id_exp_icpms_calibration_set` int NOT NULL COMMENT 'Index of the calibration set',
  `name_isotope_analyte` varchar(45) NOT NULL COMMENT 'Name of the analyte isotope',
  `name_isotope_internalstandard` varchar(45) NOT NULL COMMENT 'Name of the intenral standard isotope',
  `calibration_slope__countratio_mug_L` float NOT NULL COMMENT 'slope of the calibration curve to convert the count ratio (counts analyte per counts internal standard) to the concentration of the analyte in the experiment.',
  `delta_calibration_slope__countratio_mug_L` float NOT NULL COMMENT 'correspondiong error of the calibration slope',
  `calibration_intercept__countratio` float NOT NULL COMMENT 'y-intercept of the calibration fit in ratio of counts for analyte and internalstandard',
  `delta_calibration_intercept__countratio` float NOT NULL COMMENT 'standard deviation of y-intercept of the calibration fit in ratio of counts for analyte and internalstandard',
  `Rsquared` float NOT NULL COMMENT 'R square value for the fit. Quality parameter, but not only trust on that, check fit of calibration curve properly.',
  `calibration_method` enum('scipy.odr','scipy.optimize.curve_fit') NOT NULL COMMENT 'used method for the calibration of the icpms data.',
  `file_path_calibration_plot` varchar(254) NOT NULL COMMENT 'file path on the server to the calibration plot created by python routine.',
  `name_computer_inserted_data` varchar(45) NOT NULL COMMENT 'name of the computer on which the calibration script was performed',
  `t_inserted_data__timestamp` datetime NOT NULL COMMENT 'timestamp of the insertion routine',
  PRIMARY KEY (`id_exp_icpms_calibration_set`,`name_isotope_analyte`,`name_isotope_internalstandard`),
  CONSTRAINT `FK_exp_calib_params_id_calib_set_analyte_internalstandard` FOREIGN KEY (`id_exp_icpms_calibration_set`, `name_isotope_analyte`, `name_isotope_internalstandard`) REFERENCES `exp_icpms_analyte_internalstandard` (`id_exp_icpms_calibration_set`, `name_isotope_analyte`, `name_isotope_internalstandard`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Stores parameter for each analyte internal standard pair in a calibration set as defined in table exp_icpms_analyte_internalstandard.';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `exp_icpms_calibration_set`
--

DROP TABLE IF EXISTS `exp_icpms_calibration_set`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `exp_icpms_calibration_set` (
  `id_exp_icpms_calibration_set` int NOT NULL AUTO_INCREMENT COMMENT 'Dtabase internal index for the calibration set. A calibration set is a set of all icpms experiemtns recorded for one calibration curve. Usually for points including a blank (c_analyte = 0 mol/L) with concentrations in a range as expected for the samples are measured.',
  PRIMARY KEY (`id_exp_icpms_calibration_set`)
) ENGINE=InnoDB AUTO_INCREMENT=92 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `exp_icpms_integration`
--

DROP TABLE IF EXISTS `exp_icpms_integration`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `exp_icpms_integration` (
  `id_exp_icpms` int NOT NULL COMMENT 'index of the icpms experiment',
  `name_isotope_analyte` varchar(45) NOT NULL COMMENT 'name of analyte isotope',
  `name_isotope_internalstandard` varchar(45) NOT NULL COMMENT 'name of internalstandard isotope',
  `name_analysis` varchar(45) NOT NULL COMMENT 'name of the performed analysis',
  `id_exp_ec_dataset` int NOT NULL COMMENT 'index of the ec experiment dataset as defined by exp_ec_datasets',
  `id_ana_integration` int DEFAULT NULL COMMENT 'index of the integration analysis values',
  PRIMARY KEY (`id_exp_icpms`,`name_isotope_analyte`,`name_isotope_internalstandard`,`name_analysis`,`id_exp_ec_dataset`),
  KEY `FK_exp_icpms_integration_id_ana_integration_idx` (`id_ana_integration`),
  KEY `FK_exp_icpms_integration_id_exp_icpms_idx` (`id_exp_icpms`,`name_isotope_analyte`,`name_isotope_internalstandard`) /*!80000 INVISIBLE */,
  KEY `FK_exp_icpms_integration_name_analysis_id_exp_ec_dataset` (`name_analysis`,`id_exp_ec_dataset`) COMMENT 'index to refer batch experiment to integration of online feed',
  KEY `FK_exp_icpms_integration_integ_name_analysis_id_exp_ec_dataset` (`id_exp_ec_dataset`,`name_analysis`),
  CONSTRAINT `FK_exp_icpms_integration_id_ana_integration` FOREIGN KEY (`id_ana_integration`) REFERENCES `ana_integrations` (`id_ana_integration`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `FK_exp_icpms_integration_id_exp_ec_dataset` FOREIGN KEY (`id_exp_ec_dataset`) REFERENCES `exp_ec_datasets` (`id_exp_ec_dataset`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `FK_exp_icpms_integration_id_exp_icpms` FOREIGN KEY (`id_exp_icpms`, `name_isotope_analyte`, `name_isotope_internalstandard`) REFERENCES `exp_icpms_analyte_internalstandard` (`id_exp_icpms`, `name_isotope_analyte`, `name_isotope_internalstandard`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `FK_exp_icpms_integration_integ_name_analysis_id_exp_ec_dataset` FOREIGN KEY (`id_exp_ec_dataset`, `name_analysis`) REFERENCES `exp_ec_integration` (`id_exp_ec_dataset`, `name_analysis`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='all information from integration of icpmds data integration';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Temporary view structure for view `exp_icpms_integration_expanded`
--

DROP TABLE IF EXISTS `exp_icpms_integration_expanded`;
/*!50001 DROP VIEW IF EXISTS `exp_icpms_integration_expanded`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `exp_icpms_integration_expanded` AS SELECT 
 1 AS `element`,
 1 AS `id_exp_icpms`,
 1 AS `name_isotope_analyte`,
 1 AS `name_isotope_internalstandard`,
 1 AS `id_ana_integration_icpms`,
 1 AS `name_analysis`,
 1 AS `id_exp_ec_dataset`,
 1 AS `id_data_integration_icpms_baseline`,
 1 AS `id_data_integration_icpms_begin`,
 1 AS `id_data_integration_icpms_end`,
 1 AS `t_integration_icpms_baseline__timestamp`,
 1 AS `t_integration_icpms_begin__timestamp`,
 1 AS `t_integration_icpms_end__timestamp`,
 1 AS `m_dissolved_simps__ng`,
 1 AS `m_dissolved_trapz__ng`,
 1 AS `dm_dt_offset__ng_s`,
 1 AS `no_of_datapoints_av_icpms`,
 1 AS `no_of_datapoints_rolling_icpms`,
 1 AS `auto_integration_icpms`,
 1 AS `name_exp_ec_dataset`,
 1 AS `name_sample`,
 1 AS `name_user`,
 1 AS `name_setup_icpms`,
 1 AS `t_start__timestamp_icpms_pc`,
 1 AS `t_duration__s`,
 1 AS `t_duration_planned__s`,
 1 AS `type_experiment`,
 1 AS `plasma_mode`,
 1 AS `tune_mode`,
 1 AS `num_of_scans`,
 1 AS `id_exp_icpms_calibration_set`,
 1 AS `gas_dilution_factor`,
 1 AS `name_gas_collision`,
 1 AS `flow_rate_collision__mL_min`,
 1 AS `name_gas_reaction`,
 1 AS `flow_rate_reaction__mL_min`,
 1 AS `comment`,
 1 AS `name_computer_inserted_data`,
 1 AS `file_path_rawdata`,
 1 AS `batch_name`,
 1 AS `t_inserted_data__timestamp`,
 1 AS `file_name_rawdata`,
 1 AS `t_start_delaycorrected__timestamp_sfc_pc`,
 1 AS `t_end_delaycorrected__timestamp_sfc_pc`,
 1 AS `name_setup_sfc`,
 1 AS `t_start__timestamp_sfc_pc`,
 1 AS `t_delay__s`,
 1 AS `flow_rate_real__mul_min`,
 1 AS `calibration_slope__countratio_mug_L`,
 1 AS `delta_calibration_slope__countratio_mug_L`,
 1 AS `calibration_intercept__countratio`,
 1 AS `delta_calibration_intercept__countratio`,
 1 AS `Rsquared`,
 1 AS `calibration_method`,
 1 AS `file_path_calibration_plot`,
 1 AS `name_computer_inserted_calibration_data`,
 1 AS `t_inserted_calibration_data__timestamp`,
 1 AS `name_isotope`,
 1 AS `M__g_mol`,
 1 AS `n_dissolved_simps__mol`,
 1 AS `n_dissolved_trapz__mol`*/;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `exp_icpms_sfc`
--

DROP TABLE IF EXISTS `exp_icpms_sfc`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `exp_icpms_sfc` (
  `id_exp_icpms` int NOT NULL COMMENT 'Index of the icpms experiment',
  `t_delay__s` float NOT NULL DEFAULT '0' COMMENT 'Time delay between SFC and ICP-MS by influenced tubing diameter and electrolyte flowrate. Usually derived by processing.icpms_update_exp.update_t_delay__s',
  `t_start__timestamp_sfc_pc` datetime(6) NOT NULL COMMENT 'timestamp of the measurement start from the sfc computer. Necessary to sync EC with MS data. 1 ms in precision.',
  `name_setup_sfc` varchar(45) NOT NULL COMMENT 'name of the sfc setup used. Necessary to identifiy which SFC experiemtns belong to the icpms measurement.',
  `flow_rate_real__mul_min` decimal(5,2) DEFAULT NULL COMMENT 'actual flow rate as determined through external experiment (for instance mass loss in vial over time). Max 99 999 µL/min with precision 0.1 µL/min. ',
  `t_start_shift__s` float DEFAULT NULL COMMENT 'shift of the start time in respect to the ec start time',
  `t_end_shift__s` float DEFAULT NULL COMMENT 'shift of the end time in respect to the ec end time',
  `ISTD_fit_confidence_interval` float DEFAULT NULL COMMENT 'confidence interval of which data is selected for the ISTD fit',
  `t_updated_t_delay__timestamp` datetime(6) DEFAULT NULL COMMENT 'timestamp of the manual delay time correction, as performed by processing.icpms_update_exp.update_t_delay__s',
  `file_path_plot_update_t_delay` varchar(254) DEFAULT NULL COMMENT 'file path on server to the result plot of the update_t_delay__s routine',
  `t_updated_ISTD_fit__timestamp` datetime(6) DEFAULT NULL COMMENT 'timestamp of the ISTD fitting routine, as performed by processing.icpms_update_exp.update_counts_internalstandard_fitted',
  `file_path_plot_update_ISTD_fit` varchar(254) DEFAULT NULL COMMENT 'file path on server to the result plot of the ISTD fitting routine',
  PRIMARY KEY (`id_exp_icpms`),
  KEY `FK_exp_icpms_sfc_name_setup_sfc_idx` (`name_setup_sfc`),
  CONSTRAINT `FK_exp_icpms_sfc_id_exp_icpms` FOREIGN KEY (`id_exp_icpms`) REFERENCES `exp_icpms` (`id_exp_icpms`),
  CONSTRAINT `FK_exp_icpms_sfc_name_setup_sfc` FOREIGN KEY (`name_setup_sfc`) REFERENCES `setups_sfc` (`name_setup_sfc`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Parameters specific for sfc-icp-ms experiments';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `exp_icpms_sfc_batch`
--

DROP TABLE IF EXISTS `exp_icpms_sfc_batch`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `exp_icpms_sfc_batch` (
  `id_exp_icpms` int NOT NULL COMMENT 'index of batch icpms experiment',
  `name_setup_sfc` varchar(45) NOT NULL COMMENT 'name of the used sfc setup',
  `location` enum('top','bottom') NOT NULL COMMENT 'sfc location of the electrolyte flow used to collect',
  `t_delay__s` float DEFAULT NULL COMMENT 'delay time between sfc opening and collection vial',
  `t_start__timestamp_sfc_pc` datetime(6) DEFAULT NULL COMMENT 'timestamp at the beginning of collection',
  `t_end__timestamp_sfc_pc` datetime(6) DEFAULT NULL COMMENT 'timestamp at the end of collection',
  `m_start__g` float DEFAULT NULL COMMENT 'mass of collection vial at the beginning of cololection',
  `m_end__g` float DEFAULT NULL COMMENT 'mass of collection vial at the end of cololection',
  `density__g_mL` float DEFAULT '1' COMMENT 'density of the batch sample. Necessary to calculate the flowrate.',
  `comment` varchar(254) DEFAULT NULL COMMENT 'use comment',
  `id_exp_icpms_sfc_online` int DEFAULT NULL COMMENT 'index of the icpms experiment which was recorded onlinbe during the batch measurement. Could be derived from timestamps or  filled by user',
  `name_analysis` varchar(45) DEFAULT NULL COMMENT 'name of the analysis, to directly compare to integration results',
  `id_exp_ec_dataset` int DEFAULT NULL COMMENT 'index of the corresponding ec dataset  to directly compare to integration results and  used for stability number calculation',
  PRIMARY KEY (`id_exp_icpms`),
  KEY `FK_exp_icpms_sfc_batch_name_setup_sfc_idx` (`name_setup_sfc`),
  KEY `FK_exp_icpms_integration_name_analysis_id_exp_ec_dataset_idx` (`name_analysis`,`id_exp_ec_dataset`),
  KEY `FK_exp_icpms_id_exp_icpms_sfc_online_idx` (`id_exp_icpms_sfc_online`),
  CONSTRAINT `FK_exp_icpms_id_exp_icpms_sfc_online` FOREIGN KEY (`id_exp_icpms_sfc_online`) REFERENCES `exp_icpms_sfc` (`id_exp_icpms`),
  CONSTRAINT `FK_exp_icpms_sfc_batch_id_exp_icpms` FOREIGN KEY (`id_exp_icpms`) REFERENCES `exp_icpms` (`id_exp_icpms`),
  CONSTRAINT `FK_exp_icpms_sfc_batch_integ_name_analysis_id_exp_ec_dataset` FOREIGN KEY (`name_analysis`, `id_exp_ec_dataset`) REFERENCES `exp_icpms_integration` (`name_analysis`, `id_exp_ec_dataset`) ON UPDATE CASCADE,
  CONSTRAINT `FK_exp_icpms_sfc_batch_name_setup_sfc` FOREIGN KEY (`name_setup_sfc`) REFERENCES `setups_sfc` (`name_setup_sfc`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='storing experimental parameters for sfc batch experiments';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Temporary view structure for view `exp_icpms_sfc_batch_expanded`
--

DROP TABLE IF EXISTS `exp_icpms_sfc_batch_expanded`;
/*!50001 DROP VIEW IF EXISTS `exp_icpms_sfc_batch_expanded`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `exp_icpms_sfc_batch_expanded` AS SELECT 
 1 AS `id_exp_icpms`,
 1 AS `name_isotope_analyte`,
 1 AS `name_isotope_internalstandard`,
 1 AS `id_exp_icpms_calibration_set`,
 1 AS `id_exp_icpms_sfc_online`,
 1 AS `name_analysis`,
 1 AS `id_exp_ec_dataset`,
 1 AS `name_exp_ec_dataset`,
 1 AS `name_setup_sfc`,
 1 AS `location`,
 1 AS `t_delay__s`,
 1 AS `t_start__timestamp_sfc_pc`,
 1 AS `t_end__timestamp_sfc_pc`,
 1 AS `t_start_delaycorrected__timestamp_sfc_pc`,
 1 AS `t_end_delaycorrected__timestamp_sfc_pc`,
 1 AS `m_start__g`,
 1 AS `m_end__g`,
 1 AS `density__g_mL`,
 1 AS `comment`,
 1 AS `name_sample`,
 1 AS `name_user`,
 1 AS `name_setup_icpms`,
 1 AS `t_start__timestamp_icpms_pc`,
 1 AS `t_duration__s`,
 1 AS `t_duration_planned__s`,
 1 AS `type_experiment`,
 1 AS `plasma_mode`,
 1 AS `tune_mode`,
 1 AS `num_of_scans`,
 1 AS `gas_dilution_factor`,
 1 AS `name_gas_collision`,
 1 AS `flow_rate_collision__mL_min`,
 1 AS `name_gas_reaction`,
 1 AS `flow_rate_reaction__mL_min`,
 1 AS `name_computer_inserted_data`,
 1 AS `file_path_rawdata`,
 1 AS `t_inserted_data__timestamp`,
 1 AS `file_name_rawdata`,
 1 AS `batch_name`,
 1 AS `c_analyte__mug_L`,
 1 AS `c_internalstandard__mug_L`,
 1 AS `t_integration_analyte__s`,
 1 AS `t_integration_internalstandard__s`,
 1 AS `a_is__countratio`,
 1 AS `a_is_std__countratio`,
 1 AS `calibration_slope__countratio_mug_L`,
 1 AS `delta_calibration_slope__countratio_mug_L`,
 1 AS `calibration_intercept__countratio`,
 1 AS `delta_calibration_intercept__countratio`,
 1 AS `Rsquared`,
 1 AS `calibration_method`,
 1 AS `file_path_calibration_plot`,
 1 AS `name_computer_inserted_calibration_data`,
 1 AS `t_inserted_calibration_data__timestamp`,
 1 AS `Delta_t__s`,
 1 AS `flow_rate_real__mul_min`,
 1 AS `c_a__mug_L`,
 1 AS `dm_dt__ng_s`,
 1 AS `m_batch__ng`,
 1 AS `n_batch__mol`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `exp_icpms_sfc_expanded`
--

DROP TABLE IF EXISTS `exp_icpms_sfc_expanded`;
/*!50001 DROP VIEW IF EXISTS `exp_icpms_sfc_expanded`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `exp_icpms_sfc_expanded` AS SELECT 
 1 AS `id_exp_icpms`,
 1 AS `name_sample`,
 1 AS `name_user`,
 1 AS `name_setup_icpms`,
 1 AS `t_start__timestamp_icpms_pc`,
 1 AS `t_duration__s`,
 1 AS `t_duration_planned__s`,
 1 AS `type_experiment`,
 1 AS `plasma_mode`,
 1 AS `tune_mode`,
 1 AS `num_of_scans`,
 1 AS `id_exp_icpms_calibration_set`,
 1 AS `gas_dilution_factor`,
 1 AS `name_gas_collision`,
 1 AS `flow_rate_collision__mL_min`,
 1 AS `name_gas_reaction`,
 1 AS `flow_rate_reaction__mL_min`,
 1 AS `comment`,
 1 AS `name_computer_inserted_data`,
 1 AS `file_path_rawdata`,
 1 AS `t_inserted_data__timestamp`,
 1 AS `file_name_rawdata`,
 1 AS `batch_name`,
 1 AS `t_start_delaycorrected__timestamp_sfc_pc`,
 1 AS `t_end_delaycorrected__timestamp_sfc_pc`,
 1 AS `name_setup_sfc`,
 1 AS `t_start__timestamp_sfc_pc`,
 1 AS `t_delay__s`,
 1 AS `flow_rate_real__mul_min`,
 1 AS `t_start_shift__s`,
 1 AS `t_end_shift__s`,
 1 AS `name_isotope_analyte`,
 1 AS `name_isotope_internalstandard`,
 1 AS `calibration_slope__countratio_mug_L`,
 1 AS `delta_calibration_slope__countratio_mug_L`,
 1 AS `calibration_intercept__countratio`,
 1 AS `delta_calibration_intercept__countratio`,
 1 AS `Rsquared`,
 1 AS `calibration_method`,
 1 AS `file_path_calibration_plot`,
 1 AS `name_computer_inserted_calibration_data`,
 1 AS `t_inserted_calibration_data__timestamp`*/;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `exp_sfc`
--

DROP TABLE IF EXISTS `exp_sfc`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `exp_sfc` (
  `id_exp_sfc` int NOT NULL AUTO_INCREMENT COMMENT 'index for each sfc experiment (ec, compression) used for the database internally to connect to other tables (exp_ec, data_ec, flow_cell_assemblies,...) not important for the user. Rather identifiy your experiment by your experimental parameters!',
  `name_user` varchar(40) NOT NULL COMMENT 'name of the user who performed the experiment',
  `name_setup_sfc` varchar(40) NOT NULL COMMENT 'name of the setup at which the sfc experiment is performed',
  `t_start__timestamp` varchar(45) DEFAULT NULL COMMENT 'start time of the experiment',
  `t_end__timestamp` varchar(45) DEFAULT NULL COMMENT 'end of data acquisitoin. If not inserted by software will be updated by stored procedure.',
  `rawdata_path` varchar(254) NOT NULL COMMENT 'path to the files on the lab computer',
  `rawdata_computer` varchar(45) NOT NULL COMMENT 'name of the computer which performed the measurements',
  `id_ML` int NOT NULL COMMENT 'index of the macro list / batch list as created by sfc software',
  `id_ML_technique` int NOT NULL COMMENT 'index of the technique within the macro list / batch list. When adding a "Set" technique to the batch list in SFC Software this will be transformed to the corresponding parameters and the index number will be skipped. So it is normal that the id_ML_technique in a batch list has some numbers missing.',
  `id_sample` int NOT NULL COMMENT 'id of the used sample (see samples table)',
  `id_spot` int NOT NULL COMMENT 'id of the used spot on the sample (see spots table)',
  `force__N` decimal(6,3) NOT NULL COMMENT 'force with which the linear axis pushes against the SFC. Maximum 999 N and 0.001 N (as limited by Labview Software)',
  `T_stage__degC` float DEFAULT NULL COMMENT 'temperature of the stage in degree celsius. NULL for room temperature.',
  `interrupted` tinyint DEFAULT NULL COMMENT 'Boolean (True(1) / False(0)) wether measurement has been interrupted (=stopped) by useror software',
  `labview_sfc_version` varchar(45) NOT NULL COMMENT 'Version of the SFC Software with which the data was recorded.',
  `db_version` varchar(45) NOT NULL DEFAULT '0.11' COMMENT 'Version of the database in which the data was inserted.',
  `comment` varchar(254) DEFAULT NULL COMMENT 'user comment for any information not implemented to the database structure',
  PRIMARY KEY (`id_exp_sfc`),
  UNIQUE KEY `UNIQUE_rawdata_path_computer_id_ML` (`rawdata_computer`,`rawdata_path`,`id_ML_technique`),
  UNIQUE KEY `UNIQUE_timestamp_setup` (`t_start__timestamp`,`name_setup_sfc`),
  KEY `FK_exp_sfc_user` (`name_user`),
  KEY `FK_exp_sfc_setup_sfc` (`name_setup_sfc`),
  KEY `FK_exp_sfc_id_samplespot_idx` (`id_sample`,`id_spot`),
  CONSTRAINT `FK_exp_sfc_id_samplespot_idx` FOREIGN KEY (`id_sample`, `id_spot`) REFERENCES `spots` (`id_sample`, `id_spot`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `FK_exp_sfc_setup_sfc` FOREIGN KEY (`name_setup_sfc`) REFERENCES `setups_sfc` (`name_setup_sfc`),
  CONSTRAINT `FK_exp_sfc_user` FOREIGN KEY (`name_user`) REFERENCES `users` (`name_user`) ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=8287 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='parameter of an scanning flow cell experiment. For parameters which can hold more than one value per experiment (for instance multiple gas flows in one experiment) are located in other tables connected to the exp_sfc table via the id_exp_sfc. Same holds true for specific ec parameters (exp_ec) and different ec techniques such as CV, PEIS , GEIS,... with technique specific parameters. All parameters of electrochemical sfc exxperiments can be found combined in one table in the corresponding view "exp_ec_expanded". It is recommended to use this one for selecting data to circumvent multiple join statements in the select query.';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `flow_cell_assemblies`
--

DROP TABLE IF EXISTS `flow_cell_assemblies`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `flow_cell_assemblies` (
  `id_exp_sfc` int NOT NULL COMMENT 'connects flow cell assembly parameter to the SFC experiment (exp_sfc)',
  `location` enum('top','bottom') NOT NULL COMMENT 'Separated data entries for flow cells approached from top or bottom of the sample. Other axis are not supported yet, request feature if necessary.',
  `name_flow_cell` varchar(45) NOT NULL COMMENT 'Identifier of the flow cell used.',
  `id_sealing` int DEFAULT NULL COMMENT 'Identifier of th esealing used (optional)',
  `id_PTL` int DEFAULT NULL COMMENT 'Identifier of the porous transport layer (PTL) used (optional)',
  PRIMARY KEY (`id_exp_sfc`,`location`),
  KEY `FK_flow_cell_idx` (`name_flow_cell`),
  KEY `FK_id_PTL_idx` (`id_PTL`),
  KEY `FK_id_sealings_idx` (`id_sealing`),
  CONSTRAINT `FK_flow_cell` FOREIGN KEY (`name_flow_cell`) REFERENCES `flow_cells` (`name_flow_cell`),
  CONSTRAINT `FK_id_exp_ec_flow_cell_assemblies` FOREIGN KEY (`id_exp_sfc`) REFERENCES `exp_sfc` (`id_exp_sfc`),
  CONSTRAINT `FK_id_PTL` FOREIGN KEY (`id_PTL`) REFERENCES `porous_transport_layers` (`id_PTL`),
  CONSTRAINT `FK_id_sealings` FOREIGN KEY (`id_sealing`) REFERENCES `sealings` (`id_sealing`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='holds information on flow cells and additional parts used in the SFC experiment separated into parts above and below the sample. Above the sample (location = top) which is the commonly used SFC method with a flow cell from the top.  Below the sample (location=bottom) especially introduced for the GDE-SFC to support flow of electrolyte or gas from the back of the sample.';
/*!40101 SET character_set_client = @saved_cs_client */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `flow_cell_assemblies_AFTER_INSERT` AFTER INSERT ON `flow_cell_assemblies` FOR EACH ROW BEGIN
#	IF (SELECT COUNT(*) 
#		FROM exp_ec
#		WHERE id_exp_ec NOT IN (SELECT id_exp_ec FROM flow_cell_assemblies)) > 0
#	THEN
 #       SET @message = CONCAT('Integrity Error. Each id_exp_ec must have one entry in flow_cell_assemblies. Not fulfilled for:', 
	#				(SELECT substring_index(group_concat(e.id_exp_ec SEPARATOR ','), ',', 55) 
#                    FROM exp_ec e
#					WHERE id_exp_ec NOT IN (SELECT id_exp_ec FROM flow_cell_assemblies)));
#        signal sqlstate '23000' set message_text = @message;#'Duplicate entries in exp_ec_technique tables for id_exp_ec';
#    END IF;
    # Current problem: python script not executable as all exp_Ecs are first inserted than corresponding flow_cell_assemblies, lead to error if one tdems file contains > 1 technique
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `flow_cells`
--

DROP TABLE IF EXISTS `flow_cells`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `flow_cells` (
  `name_flow_cell` varchar(40) NOT NULL COMMENT 'Unique identifier of the flow cell by given name',
  `name_user` varchar(45) NOT NULL COMMENT 'Name of the owner of the cell',
  `material` varchar(45) NOT NULL COMMENT 'Material of which the flow cell is fabricated',
  `A_opening_ideal__mm2` decimal(9,6) NOT NULL COMMENT 'ideal area of the opening of the cell as specified by the 3D model of the cell.  Maximum 999 mm2 with precision 0.000001 mm2.',
  `A_opening_real__mm2` decimal(9,6) DEFAULT NULL COMMENT 'actual real opening area as determined electrochemically by tantalum foil or equivalent measurement.  Maximum 999 mm2 with precision 0.000001 mm2.',
  `manufacture_date` date NOT NULL COMMENT 'date of manufacturing or receiving the cell',
  `CAD_file` varchar(254) NOT NULL COMMENT 'filename of the corrsponding CAD file including the file path',
  `comment` text COMMENT 'user comment',
  PRIMARY KEY (`name_flow_cell`),
  UNIQUE KEY `name_flow_cell` (`name_flow_cell`),
  KEY `FK_flow_cells_name_user_idx` (`name_user`),
  CONSTRAINT `FK_flow_cells_name_user` FOREIGN KEY (`name_user`) REFERENCES `users` (`name_user`) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Inventory of flow cells capable to supply gas or electrolyte flow to the sample from top (connected to force sensor) or bottom (connected to stage). Can but does not have to have connections for electrodes.';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `flow_electrolyte`
--

DROP TABLE IF EXISTS `flow_electrolyte`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `flow_electrolyte` (
  `id_exp_sfc` int NOT NULL COMMENT 'connects electrolyte flow specific parameters to electrochemical experiment (exp_ec). There has to be a matching entry (id_exp_Ec+location) in the flow_cell_assmblies table.',
  `location` enum('top','bottom') NOT NULL COMMENT 'defines whether the electrolyte flow approaches the sample from top or bottom. There has to be a matching entry (id_exp_Ec+location) in the flow_cell_assmblies table.',
  `id_pump_in` int DEFAULT NULL COMMENT 'Identifier of the input peristaltic pump',
  `id_tubing_in` int DEFAULT NULL COMMENT 'Identifier of the input tubing used in the peristaltic pump',
  `pump_rate_in__rpm` int DEFAULT NULL COMMENT 'Value of the input pump rate as set in labview software',
  `id_pump_out` int NOT NULL COMMENT 'Identifier of the output peristaltic pump',
  `id_tubing_out` int NOT NULL COMMENT 'Identifier of the output tubing used in the peristaltic pump',
  `pump_rate_out__rpm` int DEFAULT NULL COMMENT 'Value of the output pump rate as set in labview software',
  `flow_rate_real__mul_min` decimal(6,1) DEFAULT NULL COMMENT 'actual flow rate as determined through external experiment (for instance mass loss over time). Max 99 999 µL/min with precision 0.1 µL/min. ',
  `name_electrolyte` varchar(45) NOT NULL COMMENT 'Name of the electrolyte salt in DI water',
  `c_electrolyte__mol_L` decimal(8,6) NOT NULL COMMENT 'concentration of the electrolyte salt in DI water. Limits of numbers are: 99 mol/L and 1 µmol/L. If limits are exceeded please consult db admin to change data type!',
  `T_electrolyte__degC` decimal(5,2) DEFAULT NULL COMMENT 'Temperature of the electrolyte in degree celsius. NULL for room temperature. Max 999 °C with 0.01 °C precision.',
  PRIMARY KEY (`id_exp_sfc`,`location`),
  KEY `FK_pump_in` (`id_pump_in`),
  KEY `FK_tubing_in` (`id_tubing_in`),
  KEY `FK_pump_out` (`id_pump_out`),
  KEY `FK_tubing_out` (`id_tubing_out`),
  KEY `FK_name_electrolyte` (`name_electrolyte`),
  CONSTRAINT `FK_flow_electrolyte_id_exp_ec_location` FOREIGN KEY (`id_exp_sfc`, `location`) REFERENCES `flow_cell_assemblies` (`id_exp_sfc`, `location`),
  CONSTRAINT `FK_name_electrolyte` FOREIGN KEY (`name_electrolyte`) REFERENCES `electrolytes` (`name_electrolyte`),
  CONSTRAINT `FK_pump_in` FOREIGN KEY (`id_pump_in`) REFERENCES `peristaltic_pumps` (`id_pump`),
  CONSTRAINT `FK_pump_out` FOREIGN KEY (`id_pump_out`) REFERENCES `peristaltic_pumps` (`id_pump`),
  CONSTRAINT `FK_tubing_in` FOREIGN KEY (`id_tubing_in`) REFERENCES `peristaltic_tubings` (`id_tubing`),
  CONSTRAINT `FK_tubing_out` FOREIGN KEY (`id_tubing_out`) REFERENCES `peristaltic_tubings` (`id_tubing`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='parameters of the electrolyte flow(s) within an SFC experiment. Multiple entries for experiments with multiple electrolyte flows (for PTL-SFC)';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `flow_gas`
--

DROP TABLE IF EXISTS `flow_gas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `flow_gas` (
  `id_exp_sfc` int NOT NULL COMMENT 'connects gas flow specific parameters to electrochemical experiment (exp_ec). There has to be a matching entry (id_exp_Ec+location) in the flow_cell_assmblies table.',
  `location` enum('top','bottom') NOT NULL COMMENT 'defines whether the gas flow approaches the sample from top or bottom. There has to be a matching entry (id_exp_Ec+location) in the flow_cell_assmblies table.',
  `function` enum('Arring','purgevial','main') NOT NULL COMMENT 'determines function of gas flow (arring, purge vial for electrolyte flow, main gas to the sample (for GDE-SFC)). Please request feature if other functions (for instance Ar mix) are necessary.',
  `name_gas` varchar(45) NOT NULL COMMENT 'Name of the gas',
  `flow_rate__mL_min` float DEFAULT NULL COMMENT 'flow rate of the gas as set in MFC with SFC software',
  PRIMARY KEY (`id_exp_sfc`,`location`,`function`),
  KEY `FK_name_gas` (`name_gas`),
  CONSTRAINT `FK_flow_gas_id_exp_ec_location` FOREIGN KEY (`id_exp_sfc`, `location`) REFERENCES `flow_cell_assemblies` (`id_exp_sfc`, `location`),
  CONSTRAINT `FK_name_gas` FOREIGN KEY (`name_gas`) REFERENCES `gases` (`name_gas`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='parameters of the gas flow(s) within an SFC experiment. Multiple entries for experiments with multiple gas flows';
/*!40101 SET character_set_client = @saved_cs_client */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `flow_gas_AFTER_UPDATE` AFTER UPDATE ON `flow_gas` FOR EACH ROW BEGIN
CALL CheckConstraints_flow_gas();
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `gamry_set_ca_speed`
--

DROP TABLE IF EXISTS `gamry_set_ca_speed`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gamry_set_ca_speed` (
  `id_ca_speed` int NOT NULL COMMENT 'CA speed corresponding id as defined by Gamry potentiostat',
  `name` varchar(40) NOT NULL COMMENT 'name for CA speed as in SFC software',
  PRIMARY KEY (`id_ca_speed`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Relation between CA speed name and corresponding index';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `gamry_set_control_mode`
--

DROP TABLE IF EXISTS `gamry_set_control_mode`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gamry_set_control_mode` (
  `id_control_mode` int NOT NULL,
  `name` varchar(40) DEFAULT NULL,
  PRIMARY KEY (`id_control_mode`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Relation between control mode name and corresponding index';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `gamry_set_ich_filter`
--

DROP TABLE IF EXISTS `gamry_set_ich_filter`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gamry_set_ich_filter` (
  `id_ich_filter` int NOT NULL,
  `name` varchar(40) NOT NULL,
  `f_ich_filter__kHz` decimal(6,3) DEFAULT NULL,
  PRIMARY KEY (`id_ich_filter`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Relation between ich filter name, corresponding index number and frequency value';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `gamry_set_ich_range`
--

DROP TABLE IF EXISTS `gamry_set_ich_range`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gamry_set_ich_range` (
  `id_ich_range` int NOT NULL,
  `name` varchar(40) NOT NULL,
  `E_max__V` decimal(4,2) NOT NULL COMMENT 'maximum acceptable potential between working and counter electrode',
  PRIMARY KEY (`id_ich_range`),
  UNIQUE KEY `name` (`name`),
  UNIQUE KEY `e_max__V` (`E_max__V`),
  UNIQUE KEY `id_ich_range_UNIQUE` (`id_ich_range`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Relation between ich range name, corresponding index number and maximum acceptable voltage between working and counter electrode';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `gamry_set_ie_range`
--

DROP TABLE IF EXISTS `gamry_set_ie_range`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gamry_set_ie_range` (
  `id_ie_range` int NOT NULL,
  `name` varchar(40) NOT NULL,
  `I_max__A` decimal(12,11) NOT NULL COMMENT 'maximum acceptable current between working and counter electrode',
  PRIMARY KEY (`id_ie_range`),
  UNIQUE KEY `name` (`name`),
  UNIQUE KEY `i_max__A_UNIQUE` (`I_max__A`),
  UNIQUE KEY `id_ie_range_UNIQUE` (`id_ie_range`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Relation between ie ch range name, corresponding index number and maximum acceptable current between working and counter electrode';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `gamry_set_ie_stability`
--

DROP TABLE IF EXISTS `gamry_set_ie_stability`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gamry_set_ie_stability` (
  `id_ie_stability` int NOT NULL,
  `name` varchar(40) NOT NULL,
  PRIMARY KEY (`id_ie_stability`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Relation between ie stability name and corresponding index number';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `gamry_set_sampling_mode`
--

DROP TABLE IF EXISTS `gamry_set_sampling_mode`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gamry_set_sampling_mode` (
  `id_sampling_mode` int NOT NULL,
  `name` varchar(40) NOT NULL,
  PRIMARY KEY (`id_sampling_mode`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Relation between sampling mode name and corresponding index number';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `gamry_set_vch_filter`
--

DROP TABLE IF EXISTS `gamry_set_vch_filter`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gamry_set_vch_filter` (
  `id_vch_filter` int NOT NULL,
  `name` varchar(40) NOT NULL,
  `f_vch_filter__kHz` decimal(6,3) DEFAULT NULL,
  PRIMARY KEY (`id_vch_filter`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Relation between vch filter name, corresponding index number and frequency value';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `gamry_set_vch_range`
--

DROP TABLE IF EXISTS `gamry_set_vch_range`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gamry_set_vch_range` (
  `id_vch_range` int NOT NULL,
  `name` varchar(40) NOT NULL,
  `E_max__V` decimal(4,2) NOT NULL COMMENT 'maximum acceptable voltage between working and counter electrode (?).',
  PRIMARY KEY (`id_vch_range`),
  UNIQUE KEY `name` (`name`),
  UNIQUE KEY `e_max__V` (`E_max__V`),
  UNIQUE KEY `id_vch_range_UNIQUE` (`id_vch_range`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Relation between ich range name, corresponding index number and maximum acceptable voltage between working and counter electrode (?)';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `gases`
--

DROP TABLE IF EXISTS `gases`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gases` (
  `name_gas` varchar(40) NOT NULL COMMENT 'name of the used gas.',
  PRIMARY KEY (`name_gas`),
  UNIQUE KEY `name` (`name_gas`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Inventory list of available gases';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `is_exp_ec_cv`
--

DROP TABLE IF EXISTS `is_exp_ec_cv`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `is_exp_ec_cv` (
  `name_technique` varchar(15) NOT NULL,
  PRIMARY KEY (`name_technique`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Recquired for so-called super/subtype construct.';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `is_exp_ec_geis`
--

DROP TABLE IF EXISTS `is_exp_ec_geis`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `is_exp_ec_geis` (
  `name_technique` varchar(15) NOT NULL,
  PRIMARY KEY (`name_technique`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Recquired for so-called super/subtype construct.';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `is_exp_ec_ghold`
--

DROP TABLE IF EXISTS `is_exp_ec_ghold`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `is_exp_ec_ghold` (
  `name_technique` varchar(15) NOT NULL,
  PRIMARY KEY (`name_technique`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Recquired for so-called super/subtype construct.';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `is_exp_ec_gpulse`
--

DROP TABLE IF EXISTS `is_exp_ec_gpulse`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `is_exp_ec_gpulse` (
  `name_technique` varchar(15) NOT NULL,
  PRIMARY KEY (`name_technique`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Recquired for so-called super/subtype construct.';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `is_exp_ec_peis`
--

DROP TABLE IF EXISTS `is_exp_ec_peis`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `is_exp_ec_peis` (
  `name_technique` varchar(15) NOT NULL,
  PRIMARY KEY (`name_technique`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Recquired for so-called super/subtype construct.';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `is_exp_ec_phold`
--

DROP TABLE IF EXISTS `is_exp_ec_phold`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `is_exp_ec_phold` (
  `name_technique` varchar(15) NOT NULL,
  PRIMARY KEY (`name_technique`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Recquired for so-called super/subtype construct.';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `is_exp_ec_ppulse`
--

DROP TABLE IF EXISTS `is_exp_ec_ppulse`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `is_exp_ec_ppulse` (
  `name_technique` varchar(15) NOT NULL,
  PRIMARY KEY (`name_technique`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Recquired for so-called super/subtype construct.';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `is_exp_ec_ramp`
--

DROP TABLE IF EXISTS `is_exp_ec_ramp`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `is_exp_ec_ramp` (
  `name_technique` varchar(15) NOT NULL,
  PRIMARY KEY (`name_technique`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Recquired for so-called super/subtype construct.';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `isotopes`
--

DROP TABLE IF EXISTS `isotopes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `isotopes` (
  `name_isotope` varchar(45) NOT NULL COMMENT 'Name of the isotope in the formate ''element name'' ''isotope weight''',
  `element` varchar(2) NOT NULL COMMENT 'two-letter element code according to periodic table',
  PRIMARY KEY (`name_isotope`),
  KEY `FK_isotopes_element_idx` (`element`),
  CONSTRAINT `FK_isotopes_element` FOREIGN KEY (`element`) REFERENCES `elements` (`element`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='isotopes used in icpms experiments';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Temporary view structure for view `match_exp_sfc_exp_icpms`
--

DROP TABLE IF EXISTS `match_exp_sfc_exp_icpms`;
/*!50001 DROP VIEW IF EXISTS `match_exp_sfc_exp_icpms`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `match_exp_sfc_exp_icpms` AS SELECT 
 1 AS `id_exp_sfc`,
 1 AS `name_user`,
 1 AS `name_setup_sfc`,
 1 AS `name_setup_sfc_alias`,
 1 AS `name_setup_sfc_feature`,
 1 AS `name_setup_sfc_type`,
 1 AS `t_start__timestamp`,
 1 AS `t_end__timestamp`,
 1 AS `rawdata_path`,
 1 AS `rawdata_computer`,
 1 AS `id_ML`,
 1 AS `id_ML_technique`,
 1 AS `id_sample`,
 1 AS `id_spot`,
 1 AS `force__N`,
 1 AS `T_stage__degC`,
 1 AS `interrupted`,
 1 AS `labview_sfc_version`,
 1 AS `db_version`,
 1 AS `comment`,
 1 AS `ec_name_technique`,
 1 AS `ec_R_u__ohm`,
 1 AS `ec_iR_corr_in_situ__percent`,
 1 AS `ec_R_u_determining_exp_ec`,
 1 AS `ec_E_RE__VvsRHE`,
 1 AS `ec_name_RE`,
 1 AS `ec_name_RE_material`,
 1 AS `ec_name_RE_manufacturer`,
 1 AS `ec_name_RE_model`,
 1 AS `ec_name_CE`,
 1 AS `ec_name_CE_material`,
 1 AS `ec_name_CE_manufacturer`,
 1 AS `ec_name_CE_model`,
 1 AS `ec_name_device`,
 1 AS `ec_id_control_mode`,
 1 AS `ec_id_ie_range`,
 1 AS `ec_id_vch_range`,
 1 AS `ec_id_ich_range`,
 1 AS `ec_id_vch_filter`,
 1 AS `ec_id_ich_filter`,
 1 AS `ec_id_ca_speed`,
 1 AS `ec_id_ie_stability`,
 1 AS `ec_id_sampling_mode`,
 1 AS `ec_ie_range_auto`,
 1 AS `ec_vch_range_auto`,
 1 AS `ec_ich_range_auto`,
 1 AS `samples_id_sample`,
 1 AS `samples_name_sample`,
 1 AS `samples_name_user`,
 1 AS `samples_t_manufactured__timestamp`,
 1 AS `samples_comment`,
 1 AS `samples_total_loading__mg_cm2`,
 1 AS `spots_id_spot`,
 1 AS `spots_spot_size__mm2`,
 1 AS `spots_pos_x__mm`,
 1 AS `spots_pos_y__mm`,
 1 AS `spots_comment`,
 1 AS `spots_total_loading__mg_cm2`,
 1 AS `cv_E_initial__VvsRE`,
 1 AS `cv_E_apex1__VvsRE`,
 1 AS `cv_E_apex2__VvsRE`,
 1 AS `cv_E_final__VvsRE`,
 1 AS `cv_scanrate__mV_s`,
 1 AS `cv_stepsize__mV`,
 1 AS `cv_cycles`,
 1 AS `geis_f_initial__Hz`,
 1 AS `geis_f_final__Hz`,
 1 AS `geis_I_dc__A`,
 1 AS `geis_I_amplitude__A`,
 1 AS `geis_R_initialguess__ohm`,
 1 AS `geis_points_per_decade`,
 1 AS `ghold_I_hold__A`,
 1 AS `ghold_t_hold__s`,
 1 AS `ghold_t_samplerate__s`,
 1 AS `peis_f_initial__Hz`,
 1 AS `peis_f_final__Hz`,
 1 AS `peis_E_dc__VvsRE`,
 1 AS `peis_E_amplitude__VvsRE`,
 1 AS `peis_R_initialguess__ohm`,
 1 AS `peis_points_per_decade`,
 1 AS `phold_E_hold__VvsRE`,
 1 AS `phold_t_hold__s`,
 1 AS `phold_t_samplerate__s`,
 1 AS `ppulse_E_hold1__VvsRE`,
 1 AS `ppulse_E_hold2__VvsRE`,
 1 AS `ppulse_t_hold1__s`,
 1 AS `ppulse_t_hold2__s`,
 1 AS `ppulse_t_samplerate__s`,
 1 AS `ppulse_cycles`,
 1 AS `gpulse_I_hold1__A`,
 1 AS `gpulse_I_hold2__A`,
 1 AS `gpulse_t_hold1__s`,
 1 AS `gpulse_t_hold2__s`,
 1 AS `gpulse_t_samplerate__s`,
 1 AS `gpulse_cycles`,
 1 AS `ramp_E_initial__VvsRE`,
 1 AS `ramp_E_final__VvsRE`,
 1 AS `ramp_scanrate__mV_s`,
 1 AS `ramp_stepsize__mV`,
 1 AS `ramp_cycles`,
 1 AS `fc_top_name_flow_cell`,
 1 AS `fc_top_name_flow_cell_name_user`,
 1 AS `fc_top_name_flow_cell_material`,
 1 AS `fc_top_name_flow_cell_A_opening_ideal__mm2`,
 1 AS `fc_top_name_flow_cell_A_opening_real__mm2`,
 1 AS `fc_top_name_flow_cell_manufacture_date`,
 1 AS `fc_top_name_flow_cell_CAD_file`,
 1 AS `fc_top_name_flow_cell_comment`,
 1 AS `fc_top_id_sealing`,
 1 AS `fc_top_id_sealing_name_user`,
 1 AS `fc_top_id_sealing_material`,
 1 AS `fc_top_id_sealing_A_sealing__mm2`,
 1 AS `fc_top_id_sealing_A_opening__mm2`,
 1 AS `fc_top_id_sealing_thickness__mm`,
 1 AS `fc_top_id_sealing_shaping_method`,
 1 AS `fc_top_id_sealing_comment`,
 1 AS `fc_top_id_PTL`,
 1 AS `fc_top_id_PTL_name_user`,
 1 AS `fc_top_id_PTL_material`,
 1 AS `fc_top_id_PTL_thickness__mm`,
 1 AS `fc_top_id_PTL_manufacturer`,
 1 AS `fc_top_id_PTL_A_PTL__mm2`,
 1 AS `fc_top_id_PTL_shaping_method`,
 1 AS `fc_top_id_PTL_comment`,
 1 AS `fc_bottom_name_flow_cell`,
 1 AS `fc_bottom_name_flow_cell_name_user`,
 1 AS `fc_bottom_name_flow_cell_material`,
 1 AS `fc_bottom_name_flow_cell_A_opening_ideal__mm2`,
 1 AS `fc_bottom_name_flow_cell_A_opening_real__mm2`,
 1 AS `fc_bottom_name_flow_cell_manufacture_date`,
 1 AS `fc_bottom_name_flow_cell_CAD_file`,
 1 AS `fc_bottom_name_flow_cell_comment`,
 1 AS `fc_bottom_id_sealing`,
 1 AS `fc_bottom_id_sealing_name_user`,
 1 AS `fc_bottom_id_sealing_material`,
 1 AS `fc_bottom_id_sealing_A_sealing__mm2`,
 1 AS `fc_bottom_id_sealing_A_opening__mm2`,
 1 AS `fc_bottom_id_sealing_thickness__mm`,
 1 AS `fc_bottom_id_sealing_shaping_method`,
 1 AS `fc_bottom_id_sealing_comment`,
 1 AS `fc_bottom_id_PTL`,
 1 AS `fc_bottom_id_PTL_name_user`,
 1 AS `fc_bottom_id_PTL_material`,
 1 AS `fc_bottom_id_PTL_thickness__mm`,
 1 AS `fc_bottom_id_PTL_manufacturer`,
 1 AS `fc_bottom_id_PTL_A_PTL__mm2`,
 1 AS `fc_bottom_id_PTL_shaping_method`,
 1 AS `fc_bottom_id_PTL_comment`,
 1 AS `fe_top_id_pump_in`,
 1 AS `fe_top_id_pump_in_manufacturer`,
 1 AS `fe_top_id_pump_in_model`,
 1 AS `fe_top_id_pump_in_device`,
 1 AS `fe_top_id_tubing_in`,
 1 AS `fe_top_id_tubing_in_name_tubing`,
 1 AS `fe_top_id_tubing_in_inner_diameter__mm`,
 1 AS `fe_top_id_tubing_in_color_code`,
 1 AS `fe_top_id_tubing_in_manufacturer`,
 1 AS `fe_top_id_tubing_in_model`,
 1 AS `fe_top_pump_rate_in__rpm`,
 1 AS `fe_top_id_pump_out`,
 1 AS `fe_top_id_pump_out_manufacturer`,
 1 AS `fe_top_id_pump_out_model`,
 1 AS `fe_top_id_pump_out_device`,
 1 AS `fe_top_id_tubing_out`,
 1 AS `fe_top_id_tubing_out_name_tubing`,
 1 AS `fe_top_id_tubing_out_inner_diameter__mm`,
 1 AS `fe_top_id_tubing_out_color_code`,
 1 AS `fe_top_id_tubing_out_manufacturer`,
 1 AS `fe_top_id_tubing_out_model`,
 1 AS `fe_top_pump_rate_out__rpm`,
 1 AS `fe_top_flow_rate_real__mul_min`,
 1 AS `fe_top_name_electrolyte`,
 1 AS `fe_top_c_electrolyte__mol_L`,
 1 AS `fe_top_T_electrolyte__degC`,
 1 AS `fe_bottom_id_pump_in`,
 1 AS `fe_bottom_id_pump_in_manufacturer`,
 1 AS `fe_bottom_id_pump_in_model`,
 1 AS `fe_bottom_id_pump_in_device`,
 1 AS `fe_bottom_id_tubing_in`,
 1 AS `fe_bottom_id_tubing_in_name_tubing`,
 1 AS `fe_bottom_id_tubing_in_inner_diameter__mm`,
 1 AS `fe_bottom_id_tubing_in_color_code`,
 1 AS `fe_bottom_id_tubing_in_manufacturer`,
 1 AS `fe_bottom_id_tubing_in_model`,
 1 AS `fe_bottom_pump_rate_in__rpm`,
 1 AS `fe_bottom_id_pump_out`,
 1 AS `fe_bottom_id_pump_out_manufacturer`,
 1 AS `fe_bottom_id_pump_out_model`,
 1 AS `fe_bottom_id_pump_out_device`,
 1 AS `fe_bottom_id_tubing_out`,
 1 AS `fe_bottom_id_tubing_out_name_tubing`,
 1 AS `fe_bottom_id_tubing_out_inner_diameter__mm`,
 1 AS `fe_bottom_id_tubing_out_color_code`,
 1 AS `fe_bottom_id_tubing_out_manufacturer`,
 1 AS `fe_bottom_id_tubing_out_model`,
 1 AS `fe_bottom_pump_rate_out__rpm`,
 1 AS `fe_bottom_flow_rate_real__mul_min`,
 1 AS `fe_bottom_name_electrolyte`,
 1 AS `fe_bottom_c_electrolyte__mol_L`,
 1 AS `fe_bottom_T_electrolyte__degC`,
 1 AS `fg_top_Arring_name_gas`,
 1 AS `fg_top_Arring_flow_rate__mL_min`,
 1 AS `fg_top_purgevial_name_gas`,
 1 AS `fg_top_purgevial_flow_rate__mL_min`,
 1 AS `fg_top_main_name_gas`,
 1 AS `fg_top_main_flow_rate__mL_min`,
 1 AS `fg_bottom_Arring_name_gas`,
 1 AS `fg_bottom_Arring_flow_rate__mL_min`,
 1 AS `fg_bottom_purgevial_name_gas`,
 1 AS `fg_bottom_purgevial_flow_rate__mL_min`,
 1 AS `fg_bottom_main_name_gas`,
 1 AS `fg_bottom_main_flow_rate__mL_min`,
 1 AS `id_exp_icpms`,
 1 AS `DATE(t_start_delaycorrected__timestamp_sfc_pc)`,
 1 AS `t_start_delaycorrected__timestamp_sfc_pc`,
 1 AS `t_end_delaycorrected__timestamp_sfc_pc`,
 1 AS `t_duration__s`,
 1 AS `location`*/;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `peristaltic_pumps`
--

DROP TABLE IF EXISTS `peristaltic_pumps`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `peristaltic_pumps` (
  `id_pump` int NOT NULL AUTO_INCREMENT COMMENT 'Identifier of the pumps',
  `manufacturer` varchar(40) NOT NULL COMMENT 'Manufacturer company of the pump',
  `model` varchar(40) NOT NULL COMMENT 'Model name of the pump as given by manufacturer',
  `device` enum('SFC','ICP-MS') NOT NULL COMMENT 'Does the pump belong to the SFC or ICP-MS?',
  PRIMARY KEY (`id_pump`),
  UNIQUE KEY `id_pump` (`id_pump`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Inventory list of available pump types. Different pumps of the same type are treated as one entry.';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `peristaltic_tubings`
--

DROP TABLE IF EXISTS `peristaltic_tubings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `peristaltic_tubings` (
  `id_tubing` int NOT NULL AUTO_INCREMENT COMMENT 'Identifier of the tubing',
  `name_tubing` varchar(45) NOT NULL COMMENT 'Unique name of the tubing. Either by marking the tubing with a name or naming a set of peristaltic tubings with its usually used channel.',
  `inner_diameter__mm` decimal(3,2) NOT NULL COMMENT 'Inner diameter of the tubing. Macximum 9 mm with precision 0.01 mm.',
  `color_code` varchar(40) NOT NULL COMMENT 'color code as given by the manufacturer',
  `manufacturer` varchar(40) NOT NULL COMMENT 'Manufacturer company',
  `model` varchar(45) DEFAULT NULL COMMENT 'Model name as given by the manufacturer (to be able to reorder tubings)',
  PRIMARY KEY (`id_tubing`),
  UNIQUE KEY `id_tubing` (`id_tubing`),
  UNIQUE KEY `name_tubing_UNIQUE` (`name_tubing`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Inventory list of tubings used. Each tubing gets a new entry with an unique name, by that aging of the tubings can be tracked.';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `porous_transport_layers`
--

DROP TABLE IF EXISTS `porous_transport_layers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `porous_transport_layers` (
  `id_PTL` int NOT NULL AUTO_INCREMENT COMMENT 'Database internal identifier of the porous transport layer',
  `name_user` varchar(45) NOT NULL COMMENT 'Name of the owner of the PTL',
  `material` varchar(45) NOT NULL COMMENT 'element and structure type of the PTL (carbon cloth, Ti sintered particles)',
  `thickness__mm` decimal(5,3) NOT NULL COMMENT 'thickness of the PTL as given by manufacturer. Request feature if thicknesses are measured by different methods are important for your samples. Maximum thickness 99 mm, with preciision 0.001 mm.',
  `manufacturer` varchar(45) NOT NULL COMMENT 'manufacturer of the PTL material',
  `A_PTL__mm2` decimal(9,6) NOT NULL COMMENT 'Area of the cutted PTL. Maximum 999 mm2 with precision 0.000001 mm2.',
  `shaping_method` enum('punching tool','laser cutter','scissor') NOT NULL COMMENT 'Method used to cut the PTL',
  `comment` varchar(254) DEFAULT NULL COMMENT 'user comment',
  PRIMARY KEY (`id_PTL`),
  UNIQUE KEY `UNIQUE_PTL` (`material`,`thickness__mm`,`manufacturer`,`A_PTL__mm2`,`shaping_method`,`comment`),
  KEY `FK_porous_transport_layers_name_user_idx` (`name_user`),
  CONSTRAINT `FK_porous_transport_layers_name_user` FOREIGN KEY (`name_user`) REFERENCES `users` (`name_user`) ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Inventory list of porous transport layers ready to place in the SFC assembly';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `publication_exps`
--

DROP TABLE IF EXISTS `publication_exps`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `publication_exps` (
  `id_publication` varchar(45) NOT NULL COMMENT 'identifier for the publication',
  `name_table` varchar(45) NOT NULL COMMENT 'name of the experiment table from which experiments are linked to publication',
  `count_exp` int NOT NULL COMMENT 'experiments with a multiindex will have for each multiindex column one entry in the table. To ensure their relationm each experiment gets a new identifier stored as integer in this column.',
  `name_index_col` varchar(45) NOT NULL COMMENT 'name of the index column',
  `value_index_col` varchar(45) NOT NULL COMMENT 'value of the index column',
  PRIMARY KEY (`id_publication`,`name_table`,`count_exp`,`name_index_col`),
  CONSTRAINT `FK_publication_exps_id_publication` FOREIGN KEY (`id_publication`) REFERENCES `publications` (`id_publication`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='stores entries for all experiments connected to a publication. Creation of table allows for putting all different experiments into the same table no matter on the number of index column. To ensure which multiindex values belong to each other, they must have the same count_exp.';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `publications`
--

DROP TABLE IF EXISTS `publications`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `publications` (
  `id_publication` varchar(45) NOT NULL COMMENT 'identifier for the publication',
  `name_user` varchar(40) NOT NULL COMMENT 'name of the user responsible fo rthe database entr yof the publication. Usually this is the first author.',
  `path_to_jupyter_folder` varchar(254) NOT NULL COMMENT 'path to the folder in which all analysis and visualization routines are stored. All data for export/upload will be stored in subfolder /upload/ of that path.',
  `title` varchar(254) DEFAULT NULL COMMENT 'title for the publication',
  `name_journal` varchar(45) DEFAULT NULL COMMENT 'name of the journal to which the publication is submitted ',
  PRIMARY KEY (`id_publication`),
  UNIQUE KEY `UNIQUE_path` (`path_to_jupyter_folder`),
  KEY `FK_publicatoins_name_user_idx` (`name_user`),
  CONSTRAINT `FK_publicatoins_name_user` FOREIGN KEY (`name_user`) REFERENCES `users` (`name_user`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='stores informations of publications using data in the database';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `reference_electrodes`
--

DROP TABLE IF EXISTS `reference_electrodes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `reference_electrodes` (
  `name_RE` varchar(40) NOT NULL COMMENT 'unique name of the reference electrode',
  `material` varchar(45) NOT NULL COMMENT 'Material of the electrode / type of the electrode',
  `manufacturer` varchar(45) NOT NULL COMMENT 'manufacturer company',
  `model` varchar(40) NOT NULL COMMENT 'Model name as given by the manufacturer to able to reorder',
  PRIMARY KEY (`name_RE`),
  UNIQUE KEY `name` (`name_RE`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Inventory list of reference electrodes';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `samples`
--

DROP TABLE IF EXISTS `samples`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `samples` (
  `id_sample` int NOT NULL AUTO_INCREMENT COMMENT 'Database internal identifier of the sample',
  `name_sample` varchar(100) NOT NULL COMMENT 'Name of the sample. Consider unique index: ''Each user has to name his/her samples uniquely. But two users can have a sample with the same name.''',
  `name_user` varchar(40) NOT NULL COMMENT 'Name of the owner the sample who fabricated and used the sample. Consider unique index: ''Each user has to name his/her samples uniquely. But two users can have a sample with the same name.'' Please request feature, if different user own (fabricate and use) the same sample.',
  `t_manufactured__timestamp` datetime NOT NULL COMMENT 'timestamp of the sample manufacturing. Exact hour/minute of the manufacturing might be more important for automated fabrication.',
  `comment` text COMMENT 'user comment',
  `total_loading__mg_cm2` decimal(12,10) DEFAULT NULL COMMENT 'total loading in mg/cm². If you want to store the loading of a specific element/material, specifiy the composition in sample_compositon (or spots_composition if composition deviates across sample). Maximum 10 with precision 0.0001',
  PRIMARY KEY (`id_sample`),
  UNIQUE KEY `name_sample_user_UNIQUE` (`name_sample`,`name_user`) COMMENT 'Each user has to name his/her samples uniquely. But two users can have a sample with the same name.',
  KEY `FK_samples_users` (`name_user`),
  CONSTRAINT `FK_samples_users` FOREIGN KEY (`name_user`) REFERENCES `users` (`name_user`) ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=139 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='List of all samples manufactured for and/or used in SFC experiments';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `samples_composition`
--

DROP TABLE IF EXISTS `samples_composition`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `samples_composition` (
  `id_sample` int NOT NULL COMMENT 'id of the sample',
  `material` varchar(100) NOT NULL COMMENT 'material can be either element, chemical compound or name of the material',
  `wt_percent` decimal(8,5) NOT NULL COMMENT 'weight percentage of the material in the spot. Maximum 100 with 0.00001 precision.',
  PRIMARY KEY (`id_sample`,`material`),
  CONSTRAINT `FK_sample_composition_id_sample` FOREIGN KEY (`id_sample`) REFERENCES `samples` (`id_sample`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='composition  of a sample is defined in weight percentage of the different materials/elements assuming the whole sample has the same composition. If not specifiy in spots_composition.';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sealings`
--

DROP TABLE IF EXISTS `sealings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sealings` (
  `id_sealing` int NOT NULL AUTO_INCREMENT COMMENT 'Database internal identifier for the sealing',
  `name_user` varchar(45) NOT NULL COMMENT 'Name of the owner of the sealing',
  `material` varchar(45) NOT NULL COMMENT 'Material of the sealing',
  `A_sealing__mm2` decimal(9,6) NOT NULL COMMENT 'area of the sealing material which will be pressed to seal. Maximum 999 mm2 with precision 0.000001 mm2.',
  `A_opening__mm2` decimal(9,6) NOT NULL COMMENT 'area of the opening of the sealing. This area can define geometric area of sample measured. Maximum 999 mm2 with precision 0.000001 mm2.',
  `thickness__mm` decimal(4,2) DEFAULT NULL COMMENT 'thickness of the sealing material in mm, NULL if not known.  Maximum thickness 99 mm, with preciision 0.001 mm.',
  `shaping_method` enum('punching tool','laser cutter','injection moulding') NOT NULL COMMENT 'shaped by punching tool (used for circular shapes), laser cutter (for any shapes), injection moulding (for liquid polymers)',
  `comment` varchar(254) DEFAULT NULL COMMENT 'user comment',
  PRIMARY KEY (`id_sealing`),
  KEY `FK_sealings_name_user_idx` (`name_user`),
  CONSTRAINT `FK_sealings_name_user` FOREIGN KEY (`name_user`) REFERENCES `users` (`name_user`) ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Inventory list of all sealings cutted and used for SFC experiments';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `setups_icpms`
--

DROP TABLE IF EXISTS `setups_icpms`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `setups_icpms` (
  `name_setup_icpms` varchar(40) NOT NULL COMMENT 'Name of the ICP-MS setup',
  `lab_no` varchar(40) NOT NULL COMMENT 'room number of the lab where the ICP-MS is located',
  `manufacturer` varchar(45) DEFAULT NULL COMMENT 'Manufacturer company',
  `model` varchar(45) DEFAULT NULL COMMENT 'Model given by manufacturer',
  PRIMARY KEY (`name_setup_icpms`),
  UNIQUE KEY `name` (`name_setup_icpms`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Inventory list of all inductively coupled plasma mass spectrometry (ICP-MS) setups';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `setups_sfc`
--

DROP TABLE IF EXISTS `setups_sfc`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `setups_sfc` (
  `name_setup_sfc` varchar(40) NOT NULL COMMENT 'Unique identifier of the SFC setup',
  `alias` varchar(40) NOT NULL COMMENT 'alias name for the setup',
  `feature` varchar(45) NOT NULL COMMENT 'special feature of the setup',
  `type` enum('SFC','RDE') NOT NULL COMMENT 'type of the setup. So far only SFC setups are implemented. Please request feature for other setups (''RDE'', ''MEA'', ''GDE'')',
  PRIMARY KEY (`name_setup_sfc`),
  UNIQUE KEY `name` (`name_setup_sfc`),
  UNIQUE KEY `alias` (`alias`),
  UNIQUE KEY `feature_UNIQUE` (`feature`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Inventory list of all scanning flow cell setups';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `spots`
--

DROP TABLE IF EXISTS `spots`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `spots` (
  `id_sample` int NOT NULL COMMENT 'Connect spot to sample',
  `id_spot` int NOT NULL COMMENT 'Identifier for the spot on a sample. As it is a secondary index column auto_increment iks not possible using MySQL. So the id_spot has to be inserted by user!',
  `spot_size__mm2` decimal(9,6) DEFAULT NULL COMMENT 'Size of the spot if applicable for example for dropcasted samples. Can be used to determine the geometric electrode area. NULL for continuous samples, geometric electrode area in this case is rather defined by opening of the cell or sealing. Maximum 999 mm2 with precision 0.000001 mm2.',
  `pos_x__mm` float DEFAULT NULL COMMENT 'x-coordinate of the spot on the sample. Coordinates relative to origin in upper left corner.',
  `pos_y__mm` float DEFAULT NULL COMMENT 'y-coordinate of the spot on the sample. Coordinates relative to origin in upper left corner.',
  `comment` text COMMENT 'user comment',
  `total_loading__mg_cm2` decimal(12,10) DEFAULT NULL COMMENT 'total loading in mg/cm² of the spot. If you want to store the loading of a specific element/material, specifiy the composition in sample_compositon (or spots_composition if composition deviates across sample). Maximum 10 with precision 0.0001',
  `m_CL__mg` float DEFAULT NULL COMMENT 'mass of the catalyst layer, usually used for dropcasting where the absolute mass is known but the spot area varies',
  `m_Decal+CL__mg` float DEFAULT NULL COMMENT 'mass of the decal sheet with catalyst layer (before decal transfer)',
  `m_Decal__mg` float DEFAULT NULL COMMENT 'mass of the decal sheet without catalyst layer after decal transfer)',
  PRIMARY KEY (`id_sample`,`id_spot`),
  UNIQUE KEY `UNIQUE_sample_spot` (`id_sample`,`id_spot`) COMMENT 'redundance to use in spots_composition',
  UNIQUE KEY `UNIQUE_coordinate` (`id_sample`,`pos_x__mm`,`pos_y__mm`) /*!80000 INVISIBLE */,
  CONSTRAINT `FK_sample_spot` FOREIGN KEY (`id_sample`) REFERENCES `samples` (`id_sample`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Inventory list of all spots an samples for SFC measurements. coordinates relative to origin in upper left corner';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Temporary view structure for view `spots_auto`
--

DROP TABLE IF EXISTS `spots_auto`;
/*!50001 DROP VIEW IF EXISTS `spots_auto`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `spots_auto` AS SELECT 
 1 AS `id_sample`,
 1 AS `id_spot`,
 1 AS `rel_x__mm`,
 1 AS `rel_y__mm`*/;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `spots_composition`
--

DROP TABLE IF EXISTS `spots_composition`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `spots_composition` (
  `id_sample` int NOT NULL COMMENT 'id of the sample',
  `id_spot` int NOT NULL COMMENT 'id of the spot on the given sample. If all spots have the same composition use table sample_composition.',
  `material` varchar(100) NOT NULL COMMENT 'material can be either element, chemical compound or name of the material',
  `wt_percent` decimal(8,5) NOT NULL COMMENT 'weight percentage of the material in the spot. Maximum 100 with 0.00001 precision. An entry here will be preferred over the loading given in sample_composition.',
  PRIMARY KEY (`id_sample`,`id_spot`,`material`),
  CONSTRAINT `FK_spots_composition_id_sample_id_spot` FOREIGN KEY (`id_sample`, `id_spot`) REFERENCES `spots` (`id_sample`, `id_spot`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='composition  of a spot on a sample is defined in weight percentage of the different materials/elements';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `name_user` varchar(40) NOT NULL COMMENT 'Full name of the user; will be used for example to identify the owner of a sample',
  PRIMARY KEY (`name_user`),
  UNIQUE KEY `name` (`name_user`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Inventory list of user of this database. Used to define the user of an experiment or owner of a sample.';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Current Database: `hte_data_documentation`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `hte_data_documentation` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;

USE `hte_data_documentation`;

--
-- Table structure for table `column_information`
--

DROP TABLE IF EXISTS `column_information`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `column_information` (
  `name_table` varchar(100) NOT NULL COMMENT 'name of the table in the database',
  `name_column` varchar(100) NOT NULL COMMENT 'name of the column in the table in the database',
  `name_inserter` varchar(45) DEFAULT NULL COMMENT 'name of the (usual) inserter - person or program which inserts data into this column. Has to be edit manually in the column_information column. The update_documentation script will give you all entries which have no inserter defined yet to update these entries.',
  `comment` longtext COMMENT 'Comment describing the meaning of the column. Comments must be edited for the corresponding table in the database schema using ''ALTER TABLE''. Afterwards the column_information column is updated using update_documentation script. Exception: For columns in views derived from multiple other columns they have to be edit manually in the columninformation table.',
  `name_axislabel__latex` varchar(255) DEFAULT NULL COMMENT 'Name of th eaxis label as expected to be printed in plots uing matplotlib. Special symbols, subscripts and superscipts can be achieved using latex similar syntax. Consult matplotlib documentation for further information. Update must be performed manually in the column_information table.',
  `table_type` enum('BASE TABLE','VIEW') DEFAULT NULL COMMENT 'Type of the table: base table = actual table in the databse; view = created table based on (multiple) other tables. Is updated automatically by the update_documentation script.',
  PRIMARY KEY (`name_table`,`name_column`),
  KEY `FK_inserter_idx` (`name_inserter`),
  CONSTRAINT `FK_inserter` FOREIGN KEY (`name_inserter`) REFERENCES `inserters` (`name_inserter`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='name_inserter has to be manually add, NULL means there is currently no insertion foreseen; comment needs to be manually add; comment only necessary for calculated columns in Views';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `inserters`
--

DROP TABLE IF EXISTS `inserters`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `inserters` (
  `name_inserter` varchar(100) NOT NULL,
  `comment` varchar(254) NOT NULL,
  PRIMARY KEY (`name_inserter`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `view_information`
--

DROP TABLE IF EXISTS `view_information`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `view_information` (
  `name_view` varchar(45) NOT NULL COMMENT 'name of the view',
  `name_base_table` varchar(45) NOT NULL COMMENT 'name of the table on which the view is based. This is used to link user requests for view data to the original experiment, the link is stored in publication_exps. Multiple netries for views possible if the view defines a link between multiple experiments.',
  PRIMARY KEY (`name_view`,`name_base_table`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='additional information for views';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Current Database: `hte_data`
--

USE `hte_data`;

--
-- Final view structure for view `data_ec_analysis`
--

/*!50001 DROP VIEW IF EXISTS `data_ec_analysis`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `data_ec_analysis` AS select `d`.`id_exp_sfc` AS `id_exp_sfc`,`d`.`id_data_ec` AS `id_data_ec`,`d`.`t__s` AS `t__s`,if((`d`.`Timestamp` is null),convert((`e`.`t_start__timestamp` + interval `d`.`t__s` second) using utf8mb4),`d`.`Timestamp`) AS `Timestamp`,`d`.`E_WE_raw__VvsRE` AS `E_WE_raw__VvsRE`,`d`.`Delta_E_WE_uncomp__V` AS `Delta_E_WE_uncomp__V`,`d`.`E_Signal__VvsRE` AS `E_Signal__VvsRE`,`d`.`I__A` AS `I__A`,`d`.`overload` AS `overload`,`d`.`cycle` AS `cycle`,if(((`e`.`ec_R_u__ohm` * `e`.`ec_iR_corr_in_situ__percent`) <> 0),((`d`.`E_WE_raw__VvsRE` + `e`.`ec_E_RE__VvsRHE`) - ((`d`.`I__A` * `e`.`ec_R_u__ohm`) * (1 - (`e`.`ec_iR_corr_in_situ__percent` / 100)))),NULL) AS `E_WE__VvsRHE`,((`d`.`E_WE_raw__VvsRE` + `e`.`ec_E_RE__VvsRHE`) + `d`.`Delta_E_WE_uncomp__V`) AS `E_WE_uncompensated__VvsRHE`,(`d`.`E_WE_raw__VvsRE` + `e`.`ec_E_RE__VvsRHE`) AS `E_WE_raw__VvsRHE`,((`d`.`I__A` * 1000) / (`e`.`spots_spot_size__mm2` / 100)) AS `j__mA_cm2geo_spot_size`,((`d`.`I__A` * 1000) / (`e`.`fc_top_name_flow_cell_A_opening_ideal__mm2` / 100)) AS `j__mA_cm2geo_fc_top_cell_Aideal`,((`d`.`I__A` * 1000) / (`e`.`fc_top_name_flow_cell_A_opening_real__mm2` / 100)) AS `j__mA_cm2geo_fc_top_cell_Areal`,((`d`.`I__A` * 1000) / (`e`.`fc_top_id_sealing_A_opening__mm2` / 100)) AS `j__mA_cm2geo_fc_top_sealing`,((`d`.`I__A` * 1000) / (`e`.`fc_top_id_PTL_A_PTL__mm2` / 100)) AS `j__mA_cm2geo_fc_top_PTL`,((`d`.`I__A` * 1000) / (`e`.`fc_bottom_name_flow_cell_A_opening_ideal__mm2` / 100)) AS `j__mA_cm2geo_fc_bottom_cell_Aideal`,((`d`.`I__A` * 1000) / (`e`.`fc_bottom_name_flow_cell_A_opening_real__mm2` / 100)) AS `j__mA_cm2geo_fc_bottom_cell_Areal`,((`d`.`I__A` * 1000) / (`e`.`fc_bottom_id_sealing_A_opening__mm2` / 100)) AS `j__mA_cm2geo_fc_bottom_sealing`,((`d`.`I__A` * 1000) / (`e`.`fc_bottom_id_PTL_A_PTL__mm2` / 100)) AS `j__mA_cm2geo_fc_bottom_PTL` from (`data_ec` `d` join `exp_ec_expanded` `e`) where (`d`.`id_exp_sfc` = `e`.`id_exp_sfc`) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `data_ec_polcurve_analysis`
--

/*!50001 DROP VIEW IF EXISTS `data_ec_polcurve_analysis`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `data_ec_polcurve_analysis` AS select `d`.`id_exp_ec_polcurve` AS `id_exp_ec_polcurve`,`d`.`id_data_ec_polcurve` AS `id_data_ec_polcurve`,`d`.`id_exp_sfc_ghold` AS `id_exp_sfc_ghold`,`d`.`id_exp_sfc_geis` AS `id_exp_sfc_geis`,`d`.`id_current_step` AS `id_current_step`,`d`.`scan_direction` AS `scan_direction`,`d`.`id_data_eis_chosen_Ru` AS `id_data_eis_chosen_Ru`,`data_eis`.`Z_real__ohm` AS `R_u__ohm`,`d`.`overload_list` AS `overload_list`,`d`.`gooddata` AS `gooddata`,`d`.`I__A` AS `I__A`,`d`.`I__A_std` AS `I__A_std`,`d`.`I_drift__A_s` AS `I_drift__A_s`,`d`.`E_WE_uncompensated__VvsRHE` AS `E_WE_uncompensated__VvsRHE`,`d`.`E_WE_uncompensated__VvsRHE_std` AS `E_WE_uncompensated__VvsRHE_std`,`d`.`E_WE_uncompensated_drift__V_s` AS `E_WE_uncompensated_drift__V_s`,(`d`.`E_WE_uncompensated__VvsRHE` - (`d`.`I__A` * `data_eis`.`Z_real__ohm`)) AS `E_WE__VvsRHE`,((`d`.`I__A` * 1000) / (`e`.`spots_spot_size__mm2` / 100)) AS `j__mA_cm2geo_spot_size`,((`d`.`I__A` * 1000) / (`e`.`fc_top_name_flow_cell_A_opening_ideal__mm2` / 100)) AS `j__mA_cm2geo_fc_top_cell_Aideal`,((`d`.`I__A` * 1000) / (`e`.`fc_top_name_flow_cell_A_opening_real__mm2` / 100)) AS `j__mA_cm2geo_fc_top_cell_Areal`,((`d`.`I__A` * 1000) / (`e`.`fc_top_id_sealing_A_opening__mm2` / 100)) AS `j__mA_cm2geo_fc_top_sealing`,((`d`.`I__A` * 1000) / (`e`.`fc_top_id_PTL_A_PTL__mm2` / 100)) AS `j__mA_cm2geo_fc_top_PTL`,((`d`.`I__A` * 1000) / (`e`.`fc_bottom_name_flow_cell_A_opening_ideal__mm2` / 100)) AS `j__mA_cm2geo_fc_bottom_cell_Aideal`,((`d`.`I__A` * 1000) / (`e`.`fc_bottom_name_flow_cell_A_opening_real__mm2` / 100)) AS `j__mA_cm2geo_fc_bottom_cell_Areal`,((`d`.`I__A` * 1000) / (`e`.`fc_bottom_id_sealing_A_opening__mm2` / 100)) AS `j__mA_cm2geo_fc_bottom_sealing`,((`d`.`I__A` * 1000) / (`e`.`fc_bottom_id_PTL_A_PTL__mm2` / 100)) AS `j__mA_cm2geo_fc_bottom_PTL`,`exp_ec_ghold`.`I_hold__A` AS `I_hold__A`,`exp_ec_ghold`.`t_hold__s` AS `t_hold__s`,`exp_ec_ghold`.`t_samplerate__s` AS `t_samplerate__s`,`exp_ec_geis`.`f_initial__Hz` AS `f_initial__Hz`,`exp_ec_geis`.`f_final__Hz` AS `f_final__Hz`,`exp_ec_geis`.`I_dc__A` AS `I_dc__A`,`exp_ec_geis`.`I_amplitude__A` AS `I_amplitude__A`,`exp_ec_geis`.`R_initialguess__ohm` AS `R_initialguess__ohm`,`exp_ec_geis`.`points_per_decade` AS `points_per_decade` from ((((`data_ec_polcurve` `d` left join `exp_ec_polcurve_expanded` `e` on((`d`.`id_exp_ec_polcurve` = `e`.`id_exp_ec_polcurve`))) left join `data_eis` on(((`d`.`id_exp_sfc_geis` = `data_eis`.`id_exp_sfc`) and (`d`.`id_data_eis_chosen_Ru` = `data_eis`.`id_data_eis`)))) left join `exp_ec_ghold` on((`d`.`id_exp_sfc_ghold` = `exp_ec_ghold`.`id_exp_sfc`))) left join `exp_ec_geis` on((`d`.`id_exp_sfc_geis` = `exp_ec_geis`.`id_exp_sfc`))) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `data_eis_analysis`
--

/*!50001 DROP VIEW IF EXISTS `data_eis_analysis`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `data_eis_analysis` AS select `d`.`id_exp_sfc` AS `id_exp_sfc`,`d`.`id_data_eis` AS `id_data_eis`,`d`.`t__s` AS `t__s`,if((`d`.`Timestamp` is null),convert((`e`.`t_start__timestamp` + interval `d`.`t__s` second) using utf8mb4),`d`.`Timestamp`) AS `Timestamp`,`d`.`f__Hz` AS `f__Hz`,`d`.`Z_real__ohm` AS `Z_real__ohm`,`d`.`minusZ_img__ohm` AS `minusZ_img__ohm`,`d`.`E_dc__VvsRE` AS `E_dc__VvsRE`,`d`.`I_dc__A` AS `I_dc__A`,(`d`.`E_dc__VvsRE` + `e`.`ec_E_RE__VvsRHE`) AS `E_WE_uncompensated__VvsRHE`,((`d`.`I_dc__A` * 1000) / (`e`.`spots_spot_size__mm2` / 100)) AS `j__mA_cm2geo_spot_size`,((`d`.`I_dc__A` * 1000) / (`e`.`fc_top_name_flow_cell_A_opening_ideal__mm2` / 100)) AS `j__mA_cm2geo_fc_top_cell_Aideal`,((`d`.`I_dc__A` * 1000) / (`e`.`fc_top_name_flow_cell_A_opening_real__mm2` / 100)) AS `j__mA_cm2geo_fc_top_cell_Areal`,((`d`.`I_dc__A` * 1000) / (`e`.`fc_top_id_sealing_A_opening__mm2` / 100)) AS `j__mA_cm2geo_fc_top_sealing`,((`d`.`I_dc__A` * 1000) / (`e`.`fc_top_id_PTL_A_PTL__mm2` / 100)) AS `j__mA_cm2geo_fc_top_PTL`,((`d`.`I_dc__A` * 1000) / (`e`.`fc_bottom_name_flow_cell_A_opening_ideal__mm2` / 100)) AS `j__mA_cm2geo_fc_bottom_cell_Aideal`,((`d`.`I_dc__A` * 1000) / (`e`.`fc_bottom_name_flow_cell_A_opening_real__mm2` / 100)) AS `j__mA_cm2geo_fc_bottom_cell_Areal`,((`d`.`I_dc__A` * 1000) / (`e`.`fc_bottom_id_sealing_A_opening__mm2` / 100)) AS `j__mA_cm2geo_fc_bottom_sealing`,((`d`.`I_dc__A` * 1000) / (`e`.`fc_bottom_id_PTL_A_PTL__mm2` / 100)) AS `j__mA_cm2geo_fc_bottom_PTL` from (`data_eis` `d` join `exp_ec_expanded` `e`) where (`d`.`id_exp_sfc` = `e`.`id_exp_sfc`) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `data_icpms_sfc_analysis`
--

/*!50001 DROP VIEW IF EXISTS `data_icpms_sfc_analysis`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `data_icpms_sfc_analysis` AS select `di`.`id_exp_icpms` AS `id_exp_icpms`,`di`.`name_isotope_analyte` AS `name_isotope_analyte`,`di`.`name_isotope_internalstandard` AS `name_isotope_internalstandard`,`di`.`id_data_icpms` AS `id_data_icpms`,`di`.`t__s` AS `t__s`,`di`.`counts_analyte` AS `counts_analyte`,`di`.`counts_internalstandard` AS `counts_internalstandard`,`di_fit`.`counts_internalstandard_fitted` AS `counts_internalstandard_fitted`,`exp_icpms_sfc_expanded`.`name_setup_sfc` AS `name_setup_sfc`,(`exp_icpms_sfc_expanded`.`t_start__timestamp_sfc_pc` + interval `di`.`t__s` second) AS `t__timestamp_sfc_pc`,((`exp_icpms_sfc_expanded`.`t_start__timestamp_sfc_pc` + interval `di`.`t__s` second) - interval `exp_icpms_sfc_expanded`.`t_delay__s` second) AS `t_delaycorrected__timestamp_sfc_pc`,(`di`.`counts_analyte` / `di_fit`.`counts_internalstandard_fitted`) AS `a_is__countratio`,(((`di`.`counts_analyte` / `di_fit`.`counts_internalstandard_fitted`) - `exp_icpms_sfc_expanded`.`calibration_intercept__countratio`) / `exp_icpms_sfc_expanded`.`calibration_slope__countratio_mug_L`) AS `c_a__mug_L`,(((((`di`.`counts_analyte` / `di_fit`.`counts_internalstandard_fitted`) - `exp_icpms_sfc_expanded`.`calibration_intercept__countratio`) / `exp_icpms_sfc_expanded`.`calibration_slope__countratio_mug_L`) * `exp_icpms_sfc_expanded`.`flow_rate_real__mul_min`) / (1000 * 60)) AS `dm_dt__ng_s` from ((`data_icpms` `di` left join `data_icpms_internalstandard_fitting` `di_fit` on(((`di`.`id_exp_icpms` = `di_fit`.`id_exp_icpms`) and (`di`.`name_isotope_analyte` = `di_fit`.`name_isotope_analyte`) and (`di`.`name_isotope_internalstandard` = `di_fit`.`name_isotope_internalstandard`) and (`di`.`id_data_icpms` = `di_fit`.`id_data_icpms`)))) join `exp_icpms_sfc_expanded` on(((`di`.`id_exp_icpms` = `exp_icpms_sfc_expanded`.`id_exp_icpms`) and (`di`.`name_isotope_analyte` = `exp_icpms_sfc_expanded`.`name_isotope_analyte`) and (`di`.`name_isotope_internalstandard` = `exp_icpms_sfc_expanded`.`name_isotope_internalstandard`)))) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `data_icpms_sfc_analysis_no_istd_fitting`
--

/*!50001 DROP VIEW IF EXISTS `data_icpms_sfc_analysis_no_istd_fitting`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `data_icpms_sfc_analysis_no_istd_fitting` AS select `di`.`id_exp_icpms` AS `id_exp_icpms`,`di`.`name_isotope_analyte` AS `name_isotope_analyte`,`di`.`name_isotope_internalstandard` AS `name_isotope_internalstandard`,`di`.`id_data_icpms` AS `id_data_icpms`,`di`.`t__s` AS `t__s`,`di`.`counts_analyte` AS `counts_analyte`,`di`.`counts_internalstandard` AS `counts_internalstandard`,`di_fit`.`counts_internalstandard_fitted` AS `counts_internalstandard_fitted`,`exp_icpms_sfc_expanded`.`name_setup_sfc` AS `name_setup_sfc`,(`exp_icpms_sfc_expanded`.`t_start__timestamp_sfc_pc` + interval `di`.`t__s` second) AS `t__timestamp_sfc_pc`,((`exp_icpms_sfc_expanded`.`t_start__timestamp_sfc_pc` + interval `di`.`t__s` second) - interval `exp_icpms_sfc_expanded`.`t_delay__s` second) AS `t_delaycorrected__timestamp_sfc_pc`,(`di`.`counts_analyte` / `di`.`counts_internalstandard`) AS `a_is__countratio`,(((`di`.`counts_analyte` / `di`.`counts_internalstandard`) - `exp_icpms_sfc_expanded`.`calibration_intercept__countratio`) / `exp_icpms_sfc_expanded`.`calibration_slope__countratio_mug_L`) AS `c_a__mug_L`,(((((`di`.`counts_analyte` / `di`.`counts_internalstandard`) - `exp_icpms_sfc_expanded`.`calibration_intercept__countratio`) / `exp_icpms_sfc_expanded`.`calibration_slope__countratio_mug_L`) * `exp_icpms_sfc_expanded`.`flow_rate_real__mul_min`) / (1000 * 60)) AS `dm_dt__ng_s` from ((`data_icpms` `di` left join `data_icpms_internalstandard_fitting` `di_fit` on(((`di`.`id_exp_icpms` = `di_fit`.`id_exp_icpms`) and (`di`.`name_isotope_analyte` = `di_fit`.`name_isotope_analyte`) and (`di`.`name_isotope_internalstandard` = `di_fit`.`name_isotope_internalstandard`) and (`di`.`id_data_icpms` = `di_fit`.`id_data_icpms`)))) join `exp_icpms_sfc_expanded` on(((`di`.`id_exp_icpms` = `exp_icpms_sfc_expanded`.`id_exp_icpms`) and (`di`.`name_isotope_analyte` = `exp_icpms_sfc_expanded`.`name_isotope_analyte`) and (`di`.`name_isotope_internalstandard` = `exp_icpms_sfc_expanded`.`name_isotope_internalstandard`)))) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `data_icpms_sfc_analysis_old`
--

/*!50001 DROP VIEW IF EXISTS `data_icpms_sfc_analysis_old`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `data_icpms_sfc_analysis_old` AS select `dip`.`id_exp_icpms` AS `id_exp_icpms`,`dip`.`name_isotope_analyte` AS `name_isotope_analyte`,`dip`.`name_isotope_internalstandard` AS `name_isotope_internalstandard`,`dip`.`id_data_icpms` AS `id_data_icpms`,`dip`.`t__s` AS `t__s`,`dip`.`counts_analyte` AS `counts_analyte`,`dip`.`counts_internalstandard` AS `counts_internalstandard`,`dip`.`name_setup_sfc` AS `name_setup_sfc`,`dip`.`t__timestamp_sfc_pc` AS `t__timestamp_sfc_pc`,`dip`.`t_delaycorrected__timestamp_sfc_pc` AS `t_delaycorrected__timestamp_sfc_pc`,`dip`.`a_is__countratio` AS `a_is__countratio`,`dip`.`c_a__mug_L` AS `c_a__mug_L`,`dip`.`dm_dt__ng_s` AS `dm_dt__ng_s`,`exp_ec_expanded_old`.`id_exp_sfc` AS `id_exp_sfc`,(`dip`.`dm_dt__ng_s` / (`exp_ec_expanded_old`.`spots_spot_size__mm2` / 100)) AS `dm_dt_S__ng_s_cm2geo_spot_size`,(`dip`.`dm_dt__ng_s` / (`exp_ec_expanded_old`.`fc_top_name_flow_cell_A_opening_ideal__mm2` / 100)) AS `dm_dt_S__ng_s_cm2geo_fc_top_cell_Aideal`,(`dip`.`dm_dt__ng_s` / (`exp_ec_expanded_old`.`fc_top_name_flow_cell_A_opening_real__mm2` / 100)) AS `dm_dt_S__ng_s_cm2geo_fc_top_cell_Areal`,(`dip`.`dm_dt__ng_s` / (`exp_ec_expanded_old`.`fc_top_id_sealing_A_opening__mm2` / 100)) AS `dm_dt_S__ng_s_cm2geo_fc_top_sealing`,(`dip`.`dm_dt__ng_s` / (`exp_ec_expanded_old`.`fc_top_id_PTL_A_PTL__mm2` / 100)) AS `dm_dt_S__ng_s_cm2geo_fc_top_PTL`,(`dip`.`dm_dt__ng_s` / (`exp_ec_expanded_old`.`fc_bottom_name_flow_cell_A_opening_ideal__mm2` / 100)) AS `dm_dt_S__ng_s_cm2geo_fc_bottom_cell_Aideal`,(`dip`.`dm_dt__ng_s` / (`exp_ec_expanded_old`.`fc_bottom_name_flow_cell_A_opening_real__mm2` / 100)) AS `dm_dt_S__ng_s_cm2geo_fc_bottom_cell_Areal`,(`dip`.`dm_dt__ng_s` / (`exp_ec_expanded_old`.`fc_bottom_id_sealing_A_opening__mm2` / 100)) AS `dm_dt_S__ng_s_cm2geo_fc_bottom_sealing`,(`dip`.`dm_dt__ng_s` / (`exp_ec_expanded_old`.`fc_bottom_id_PTL_A_PTL__mm2` / 100)) AS `dm_dt_S__ng_s_cm2geo_fc_bottom_PTL` from ((select `di`.`id_exp_icpms` AS `id_exp_icpms`,`di`.`name_isotope_analyte` AS `name_isotope_analyte`,`di`.`name_isotope_internalstandard` AS `name_isotope_internalstandard`,`di`.`id_data_icpms` AS `id_data_icpms`,`di`.`t__s` AS `t__s`,`di`.`counts_analyte` AS `counts_analyte`,`di`.`counts_internalstandard` AS `counts_internalstandard`,`exp_icpms_sfc_expanded`.`name_setup_sfc` AS `name_setup_sfc`,(`exp_icpms_sfc_expanded`.`t_start__timestamp_sfc_pc` + interval `di`.`t__s` second) AS `t__timestamp_sfc_pc`,((`exp_icpms_sfc_expanded`.`t_start__timestamp_sfc_pc` + interval `di`.`t__s` second) + interval -(`exp_icpms_sfc_expanded`.`t_delay__s`) second) AS `t_delaycorrected__timestamp_sfc_pc`,(`di`.`counts_analyte` / `di`.`counts_internalstandard`) AS `a_is__countratio`,(((`di`.`counts_analyte` / `di`.`counts_internalstandard`) - `exp_icpms_sfc_expanded`.`calibration_intercept__countratio`) / `exp_icpms_sfc_expanded`.`calibration_slope__countratio_mug_L`) AS `c_a__mug_L`,(((((`di`.`counts_analyte` / `di`.`counts_internalstandard`) - `exp_icpms_sfc_expanded`.`calibration_intercept__countratio`) / `exp_icpms_sfc_expanded`.`calibration_slope__countratio_mug_L`) * `exp_icpms_sfc_expanded`.`flow_rate_real__mul_min`) / (1000 * 60)) AS `dm_dt__ng_s` from (`data_icpms` `di` left join `exp_icpms_sfc_expanded` on(((`di`.`id_exp_icpms` = `exp_icpms_sfc_expanded`.`id_exp_icpms`) and (`di`.`name_isotope_analyte` = `exp_icpms_sfc_expanded`.`name_isotope_analyte`) and (`di`.`name_isotope_internalstandard` = `exp_icpms_sfc_expanded`.`name_isotope_internalstandard`)))) where (`exp_icpms_sfc_expanded`.`type_experiment` = 'sfc-icpms')) `dip` left join (select `exp_ec_expanded_old`.`id_exp_sfc` AS `id_exp_sfc`,`exp_ec_expanded_old`.`t_start__timestamp` AS `t_start__timestamp`,`exp_ec_expanded_old`.`t_duration__s` AS `t_duration__s`,`exp_ec_expanded_old`.`name_setup_sfc` AS `name_setup_sfc`,lead(`exp_ec_expanded_old`.`t_start__timestamp`) OVER (ORDER BY `exp_ec_expanded_old`.`t_start__timestamp` )  AS `next_t_start_timestamp`,`exp_ec_expanded_old`.`spots_spot_size__mm2` AS `spots_spot_size__mm2`,`exp_ec_expanded_old`.`fc_top_name_flow_cell_A_opening_ideal__mm2` AS `fc_top_name_flow_cell_A_opening_ideal__mm2`,`exp_ec_expanded_old`.`fc_top_name_flow_cell_A_opening_real__mm2` AS `fc_top_name_flow_cell_A_opening_real__mm2`,`exp_ec_expanded_old`.`fc_top_id_sealing_A_opening__mm2` AS `fc_top_id_sealing_A_opening__mm2`,`exp_ec_expanded_old`.`fc_top_id_PTL_A_PTL__mm2` AS `fc_top_id_PTL_A_PTL__mm2`,`exp_ec_expanded_old`.`fc_bottom_name_flow_cell_A_opening_ideal__mm2` AS `fc_bottom_name_flow_cell_A_opening_ideal__mm2`,`exp_ec_expanded_old`.`fc_bottom_name_flow_cell_A_opening_real__mm2` AS `fc_bottom_name_flow_cell_A_opening_real__mm2`,`exp_ec_expanded_old`.`fc_bottom_id_sealing_A_opening__mm2` AS `fc_bottom_id_sealing_A_opening__mm2`,`exp_ec_expanded_old`.`fc_bottom_id_PTL_A_PTL__mm2` AS `fc_bottom_id_PTL_A_PTL__mm2` from (select `exp_ec_expanded_old`.`id_exp_sfc` AS `id_exp_sfc`,`exp_ec_expanded_old`.`name_user` AS `name_user`,`exp_ec_expanded_old`.`name_setup_sfc` AS `name_setup_sfc`,`exp_ec_expanded_old`.`name_setup_sfc_alias` AS `name_setup_sfc_alias`,`exp_ec_expanded_old`.`name_setup_sfc_feature` AS `name_setup_sfc_feature`,`exp_ec_expanded_old`.`name_setup_sfc_type` AS `name_setup_sfc_type`,`exp_ec_expanded_old`.`t_start__timestamp` AS `t_start__timestamp`,`exp_ec_expanded_old`.`rawdata_path` AS `rawdata_path`,`exp_ec_expanded_old`.`rawdata_computer` AS `rawdata_computer`,`exp_ec_expanded_old`.`id_ML` AS `id_ML`,`exp_ec_expanded_old`.`id_ML_technique` AS `id_ML_technique`,`exp_ec_expanded_old`.`id_sample` AS `id_sample`,`exp_ec_expanded_old`.`id_spot` AS `id_spot`,`exp_ec_expanded_old`.`force__N` AS `force__N`,`exp_ec_expanded_old`.`T_stage__degC` AS `T_stage__degC`,`exp_ec_expanded_old`.`interrupted` AS `interrupted`,`exp_ec_expanded_old`.`labview_sfc_version` AS `labview_sfc_version`,`exp_ec_expanded_old`.`db_version` AS `db_version`,`exp_ec_expanded_old`.`comment` AS `comment`,`exp_ec_expanded_old`.`t_duration__s` AS `t_duration__s`,`exp_ec_expanded_old`.`t_end__timestamp` AS `t_end__timestamp`,`exp_ec_expanded_old`.`ec_name_technique` AS `ec_name_technique`,`exp_ec_expanded_old`.`ec_R_u__ohm` AS `ec_R_u__ohm`,`exp_ec_expanded_old`.`ec_iR_corr_in_situ__percent` AS `ec_iR_corr_in_situ__percent`,`exp_ec_expanded_old`.`ec_R_u_determining_exp_ec` AS `ec_R_u_determining_exp_ec`,`exp_ec_expanded_old`.`ec_E_RE__VvsRHE` AS `ec_E_RE__VvsRHE`,`exp_ec_expanded_old`.`ec_name_RE` AS `ec_name_RE`,`exp_ec_expanded_old`.`ec_name_RE_material` AS `ec_name_RE_material`,`exp_ec_expanded_old`.`ec_name_RE_manufacturer` AS `ec_name_RE_manufacturer`,`exp_ec_expanded_old`.`ec_name_RE_model` AS `ec_name_RE_model`,`exp_ec_expanded_old`.`ec_name_CE` AS `ec_name_CE`,`exp_ec_expanded_old`.`ec_name_CE_material` AS `ec_name_CE_material`,`exp_ec_expanded_old`.`ec_name_CE_manufacturer` AS `ec_name_CE_manufacturer`,`exp_ec_expanded_old`.`ec_name_CE_model` AS `ec_name_CE_model`,`exp_ec_expanded_old`.`ec_name_device` AS `ec_name_device`,`exp_ec_expanded_old`.`ec_id_control_mode` AS `ec_id_control_mode`,`exp_ec_expanded_old`.`ec_id_ie_range` AS `ec_id_ie_range`,`exp_ec_expanded_old`.`ec_id_vch_range` AS `ec_id_vch_range`,`exp_ec_expanded_old`.`ec_id_ich_range` AS `ec_id_ich_range`,`exp_ec_expanded_old`.`ec_id_vch_filter` AS `ec_id_vch_filter`,`exp_ec_expanded_old`.`ec_id_ich_filter` AS `ec_id_ich_filter`,`exp_ec_expanded_old`.`ec_id_ca_speed` AS `ec_id_ca_speed`,`exp_ec_expanded_old`.`ec_id_ie_stability` AS `ec_id_ie_stability`,`exp_ec_expanded_old`.`ec_id_sampling_mode` AS `ec_id_sampling_mode`,`exp_ec_expanded_old`.`ec_ie_range_auto` AS `ec_ie_range_auto`,`exp_ec_expanded_old`.`ec_vch_range_auto` AS `ec_vch_range_auto`,`exp_ec_expanded_old`.`ec_ich_range_auto` AS `ec_ich_range_auto`,`exp_ec_expanded_old`.`samples_id_sample` AS `samples_id_sample`,`exp_ec_expanded_old`.`samples_name_sample` AS `samples_name_sample`,`exp_ec_expanded_old`.`samples_name_user` AS `samples_name_user`,`exp_ec_expanded_old`.`samples_t_manufactured__timestamp` AS `samples_t_manufactured__timestamp`,`exp_ec_expanded_old`.`samples_comment` AS `samples_comment`,`exp_ec_expanded_old`.`spots_id_spot` AS `spots_id_spot`,`exp_ec_expanded_old`.`spots_spot_size__mm2` AS `spots_spot_size__mm2`,`exp_ec_expanded_old`.`spots_pos_x__mm` AS `spots_pos_x__mm`,`exp_ec_expanded_old`.`spots_pos_y__mm` AS `spots_pos_y__mm`,`exp_ec_expanded_old`.`spots_comment` AS `spots_comment`,`exp_ec_expanded_old`.`cv_E_initial__VvsRE` AS `cv_E_initial__VvsRE`,`exp_ec_expanded_old`.`cv_E_apex1__VvsRE` AS `cv_E_apex1__VvsRE`,`exp_ec_expanded_old`.`cv_E_apex2__VvsRE` AS `cv_E_apex2__VvsRE`,`exp_ec_expanded_old`.`cv_E_final__VvsRE` AS `cv_E_final__VvsRE`,`exp_ec_expanded_old`.`cv_scanrate__mV_s` AS `cv_scanrate__mV_s`,`exp_ec_expanded_old`.`cv_stepsize__mV` AS `cv_stepsize__mV`,`exp_ec_expanded_old`.`cv_cycles` AS `cv_cycles`,`exp_ec_expanded_old`.`geis_f_initial__Hz` AS `geis_f_initial__Hz`,`exp_ec_expanded_old`.`geis_f_final__Hz` AS `geis_f_final__Hz`,`exp_ec_expanded_old`.`geis_I_dc__A` AS `geis_I_dc__A`,`exp_ec_expanded_old`.`geis_I_amplitude__A` AS `geis_I_amplitude__A`,`exp_ec_expanded_old`.`geis_R_initialguess__ohm` AS `geis_R_initialguess__ohm`,`exp_ec_expanded_old`.`geis_points_per_decade` AS `geis_points_per_decade`,`exp_ec_expanded_old`.`ghold_I_hold__A` AS `ghold_I_hold__A`,`exp_ec_expanded_old`.`ghold_t_hold__s` AS `ghold_t_hold__s`,`exp_ec_expanded_old`.`ghold_t_samplerate__s` AS `ghold_t_samplerate__s`,`exp_ec_expanded_old`.`peis_f_initial__Hz` AS `peis_f_initial__Hz`,`exp_ec_expanded_old`.`peis_f_final__Hz` AS `peis_f_final__Hz`,`exp_ec_expanded_old`.`peis_E_dc__VvsRE` AS `peis_E_dc__VvsRE`,`exp_ec_expanded_old`.`peis_E_amplitude__VvsRE` AS `peis_E_amplitude__VvsRE`,`exp_ec_expanded_old`.`peis_R_initialguess__ohm` AS `peis_R_initialguess__ohm`,`exp_ec_expanded_old`.`peis_points_per_decade` AS `peis_points_per_decade`,`exp_ec_expanded_old`.`phold_E_hold__VvsRE` AS `phold_E_hold__VvsRE`,`exp_ec_expanded_old`.`phold_t_hold__s` AS `phold_t_hold__s`,`exp_ec_expanded_old`.`phold_t_samplerate__s` AS `phold_t_samplerate__s`,`exp_ec_expanded_old`.`ppulse_E_hold1__VvsRE` AS `ppulse_E_hold1__VvsRE`,`exp_ec_expanded_old`.`ppulse_E_hold2__VvsRE` AS `ppulse_E_hold2__VvsRE`,`exp_ec_expanded_old`.`ppulse_t_hold1__s` AS `ppulse_t_hold1__s`,`exp_ec_expanded_old`.`ppulse_t_hold2__s` AS `ppulse_t_hold2__s`,`exp_ec_expanded_old`.`ppulse_t_samplerate__s` AS `ppulse_t_samplerate__s`,`exp_ec_expanded_old`.`ppulse_cycles` AS `ppulse_cycles`,`exp_ec_expanded_old`.`gpulse_I_hold1__A` AS `gpulse_I_hold1__A`,`exp_ec_expanded_old`.`gpulse_I_hold2__A` AS `gpulse_I_hold2__A`,`exp_ec_expanded_old`.`gpulse_t_hold1__s` AS `gpulse_t_hold1__s`,`exp_ec_expanded_old`.`gpulse_t_hold2__s` AS `gpulse_t_hold2__s`,`exp_ec_expanded_old`.`gpulse_t_samplerate__s` AS `gpulse_t_samplerate__s`,`exp_ec_expanded_old`.`gpulse_cycles` AS `gpulse_cycles`,`exp_ec_expanded_old`.`ramp_E_initial__VvsRE` AS `ramp_E_initial__VvsRE`,`exp_ec_expanded_old`.`ramp_E_final__VvsRE` AS `ramp_E_final__VvsRE`,`exp_ec_expanded_old`.`ramp_scanrate__mV_s` AS `ramp_scanrate__mV_s`,`exp_ec_expanded_old`.`ramp_stepsize__mV` AS `ramp_stepsize__mV`,`exp_ec_expanded_old`.`ramp_cycles` AS `ramp_cycles`,`exp_ec_expanded_old`.`fc_top_name_flow_cell` AS `fc_top_name_flow_cell`,`exp_ec_expanded_old`.`fc_top_name_flow_cell_name_user` AS `fc_top_name_flow_cell_name_user`,`exp_ec_expanded_old`.`fc_top_name_flow_cell_material` AS `fc_top_name_flow_cell_material`,`exp_ec_expanded_old`.`fc_top_name_flow_cell_A_opening_ideal__mm2` AS `fc_top_name_flow_cell_A_opening_ideal__mm2`,`exp_ec_expanded_old`.`fc_top_name_flow_cell_A_opening_real__mm2` AS `fc_top_name_flow_cell_A_opening_real__mm2`,`exp_ec_expanded_old`.`fc_top_name_flow_cell_manufacture_date` AS `fc_top_name_flow_cell_manufacture_date`,`exp_ec_expanded_old`.`fc_top_name_flow_cell_CAD_file` AS `fc_top_name_flow_cell_CAD_file`,`exp_ec_expanded_old`.`fc_top_name_flow_cell_comment` AS `fc_top_name_flow_cell_comment`,`exp_ec_expanded_old`.`fc_top_id_sealing` AS `fc_top_id_sealing`,`exp_ec_expanded_old`.`fc_top_id_sealing_name_user` AS `fc_top_id_sealing_name_user`,`exp_ec_expanded_old`.`fc_top_id_sealing_material` AS `fc_top_id_sealing_material`,`exp_ec_expanded_old`.`fc_top_id_sealing_A_sealing__mm2` AS `fc_top_id_sealing_A_sealing__mm2`,`exp_ec_expanded_old`.`fc_top_id_sealing_A_opening__mm2` AS `fc_top_id_sealing_A_opening__mm2`,`exp_ec_expanded_old`.`fc_top_id_sealing_thickness__mm` AS `fc_top_id_sealing_thickness__mm`,`exp_ec_expanded_old`.`fc_top_id_sealing_shaping_method` AS `fc_top_id_sealing_shaping_method`,`exp_ec_expanded_old`.`fc_top_id_sealing_comment` AS `fc_top_id_sealing_comment`,`exp_ec_expanded_old`.`fc_top_id_PTL` AS `fc_top_id_PTL`,`exp_ec_expanded_old`.`fc_top_id_PTL_name_user` AS `fc_top_id_PTL_name_user`,`exp_ec_expanded_old`.`fc_top_id_PTL_material` AS `fc_top_id_PTL_material`,`exp_ec_expanded_old`.`fc_top_id_PTL_thickness__mm` AS `fc_top_id_PTL_thickness__mm`,`exp_ec_expanded_old`.`fc_top_id_PTL_manufacturer` AS `fc_top_id_PTL_manufacturer`,`exp_ec_expanded_old`.`fc_top_id_PTL_A_PTL__mm2` AS `fc_top_id_PTL_A_PTL__mm2`,`exp_ec_expanded_old`.`fc_top_id_PTL_shaping_method` AS `fc_top_id_PTL_shaping_method`,`exp_ec_expanded_old`.`fc_top_id_PTL_comment` AS `fc_top_id_PTL_comment`,`exp_ec_expanded_old`.`fc_bottom_name_flow_cell` AS `fc_bottom_name_flow_cell`,`exp_ec_expanded_old`.`fc_bottom_name_flow_cell_name_user` AS `fc_bottom_name_flow_cell_name_user`,`exp_ec_expanded_old`.`fc_bottom_name_flow_cell_material` AS `fc_bottom_name_flow_cell_material`,`exp_ec_expanded_old`.`fc_bottom_name_flow_cell_A_opening_ideal__mm2` AS `fc_bottom_name_flow_cell_A_opening_ideal__mm2`,`exp_ec_expanded_old`.`fc_bottom_name_flow_cell_A_opening_real__mm2` AS `fc_bottom_name_flow_cell_A_opening_real__mm2`,`exp_ec_expanded_old`.`fc_bottom_name_flow_cell_manufacture_date` AS `fc_bottom_name_flow_cell_manufacture_date`,`exp_ec_expanded_old`.`fc_bottom_name_flow_cell_CAD_file` AS `fc_bottom_name_flow_cell_CAD_file`,`exp_ec_expanded_old`.`fc_bottom_name_flow_cell_comment` AS `fc_bottom_name_flow_cell_comment`,`exp_ec_expanded_old`.`fc_bottom_id_sealing` AS `fc_bottom_id_sealing`,`exp_ec_expanded_old`.`fc_bottom_id_sealing_name_user` AS `fc_bottom_id_sealing_name_user`,`exp_ec_expanded_old`.`fc_bottom_id_sealing_material` AS `fc_bottom_id_sealing_material`,`exp_ec_expanded_old`.`fc_bottom_id_sealing_A_sealing__mm2` AS `fc_bottom_id_sealing_A_sealing__mm2`,`exp_ec_expanded_old`.`fc_bottom_id_sealing_A_opening__mm2` AS `fc_bottom_id_sealing_A_opening__mm2`,`exp_ec_expanded_old`.`fc_bottom_id_sealing_thickness__mm` AS `fc_bottom_id_sealing_thickness__mm`,`exp_ec_expanded_old`.`fc_bottom_id_sealing_shaping_method` AS `fc_bottom_id_sealing_shaping_method`,`exp_ec_expanded_old`.`fc_bottom_id_sealing_comment` AS `fc_bottom_id_sealing_comment`,`exp_ec_expanded_old`.`fc_bottom_id_PTL` AS `fc_bottom_id_PTL`,`exp_ec_expanded_old`.`fc_bottom_id_PTL_name_user` AS `fc_bottom_id_PTL_name_user`,`exp_ec_expanded_old`.`fc_bottom_id_PTL_material` AS `fc_bottom_id_PTL_material`,`exp_ec_expanded_old`.`fc_bottom_id_PTL_thickness__mm` AS `fc_bottom_id_PTL_thickness__mm`,`exp_ec_expanded_old`.`fc_bottom_id_PTL_manufacturer` AS `fc_bottom_id_PTL_manufacturer`,`exp_ec_expanded_old`.`fc_bottom_id_PTL_A_PTL__mm2` AS `fc_bottom_id_PTL_A_PTL__mm2`,`exp_ec_expanded_old`.`fc_bottom_id_PTL_shaping_method` AS `fc_bottom_id_PTL_shaping_method`,`exp_ec_expanded_old`.`fc_bottom_id_PTL_comment` AS `fc_bottom_id_PTL_comment`,`exp_ec_expanded_old`.`fe_top_id_pump_in` AS `fe_top_id_pump_in`,`exp_ec_expanded_old`.`fe_top_id_pump_in_manufacturer` AS `fe_top_id_pump_in_manufacturer`,`exp_ec_expanded_old`.`fe_top_id_pump_in_model` AS `fe_top_id_pump_in_model`,`exp_ec_expanded_old`.`fe_top_id_pump_in_device` AS `fe_top_id_pump_in_device`,`exp_ec_expanded_old`.`fe_top_id_tubing_in` AS `fe_top_id_tubing_in`,`exp_ec_expanded_old`.`fe_top_id_tubing_in_name_tubing` AS `fe_top_id_tubing_in_name_tubing`,`exp_ec_expanded_old`.`fe_top_id_tubing_in_inner_diameter__mm` AS `fe_top_id_tubing_in_inner_diameter__mm`,`exp_ec_expanded_old`.`fe_top_id_tubing_in_color_code` AS `fe_top_id_tubing_in_color_code`,`exp_ec_expanded_old`.`fe_top_id_tubing_in_manufacturer` AS `fe_top_id_tubing_in_manufacturer`,`exp_ec_expanded_old`.`fe_top_id_tubing_in_model` AS `fe_top_id_tubing_in_model`,`exp_ec_expanded_old`.`fe_top_pump_rate_in__rpm` AS `fe_top_pump_rate_in__rpm`,`exp_ec_expanded_old`.`fe_top_id_pump_out` AS `fe_top_id_pump_out`,`exp_ec_expanded_old`.`fe_top_id_pump_out_manufacturer` AS `fe_top_id_pump_out_manufacturer`,`exp_ec_expanded_old`.`fe_top_id_pump_out_model` AS `fe_top_id_pump_out_model`,`exp_ec_expanded_old`.`fe_top_id_pump_out_device` AS `fe_top_id_pump_out_device`,`exp_ec_expanded_old`.`fe_top_id_tubing_out` AS `fe_top_id_tubing_out`,`exp_ec_expanded_old`.`fe_top_id_tubing_out_name_tubing` AS `fe_top_id_tubing_out_name_tubing`,`exp_ec_expanded_old`.`fe_top_id_tubing_out_inner_diameter__mm` AS `fe_top_id_tubing_out_inner_diameter__mm`,`exp_ec_expanded_old`.`fe_top_id_tubing_out_color_code` AS `fe_top_id_tubing_out_color_code`,`exp_ec_expanded_old`.`fe_top_id_tubing_out_manufacturer` AS `fe_top_id_tubing_out_manufacturer`,`exp_ec_expanded_old`.`fe_top_id_tubing_out_model` AS `fe_top_id_tubing_out_model`,`exp_ec_expanded_old`.`fe_top_pump_rate_out__rpm` AS `fe_top_pump_rate_out__rpm`,`exp_ec_expanded_old`.`fe_top_flow_rate_real__mul_min` AS `fe_top_flow_rate_real__mul_min`,`exp_ec_expanded_old`.`fe_top_name_electrolyte` AS `fe_top_name_electrolyte`,`exp_ec_expanded_old`.`fe_top_c_electrolyte__mol_L` AS `fe_top_c_electrolyte__mol_L`,`exp_ec_expanded_old`.`fe_top_T_electrolyte__degC` AS `fe_top_T_electrolyte__degC`,`exp_ec_expanded_old`.`fe_bottom_id_pump_in` AS `fe_bottom_id_pump_in`,`exp_ec_expanded_old`.`fe_bottom_id_pump_in_manufacturer` AS `fe_bottom_id_pump_in_manufacturer`,`exp_ec_expanded_old`.`fe_bottom_id_pump_in_model` AS `fe_bottom_id_pump_in_model`,`exp_ec_expanded_old`.`fe_bottom_id_pump_in_device` AS `fe_bottom_id_pump_in_device`,`exp_ec_expanded_old`.`fe_bottom_id_tubing_in` AS `fe_bottom_id_tubing_in`,`exp_ec_expanded_old`.`fe_bottom_id_tubing_in_name_tubing` AS `fe_bottom_id_tubing_in_name_tubing`,`exp_ec_expanded_old`.`fe_bottom_id_tubing_in_inner_diameter__mm` AS `fe_bottom_id_tubing_in_inner_diameter__mm`,`exp_ec_expanded_old`.`fe_bottom_id_tubing_in_color_code` AS `fe_bottom_id_tubing_in_color_code`,`exp_ec_expanded_old`.`fe_bottom_id_tubing_in_manufacturer` AS `fe_bottom_id_tubing_in_manufacturer`,`exp_ec_expanded_old`.`fe_bottom_id_tubing_in_model` AS `fe_bottom_id_tubing_in_model`,`exp_ec_expanded_old`.`fe_bottom_pump_rate_in__rpm` AS `fe_bottom_pump_rate_in__rpm`,`exp_ec_expanded_old`.`fe_bottom_id_pump_out` AS `fe_bottom_id_pump_out`,`exp_ec_expanded_old`.`fe_bottom_id_pump_out_manufacturer` AS `fe_bottom_id_pump_out_manufacturer`,`exp_ec_expanded_old`.`fe_bottom_id_pump_out_model` AS `fe_bottom_id_pump_out_model`,`exp_ec_expanded_old`.`fe_bottom_id_pump_out_device` AS `fe_bottom_id_pump_out_device`,`exp_ec_expanded_old`.`fe_bottom_id_tubing_out` AS `fe_bottom_id_tubing_out`,`exp_ec_expanded_old`.`fe_bottom_id_tubing_out_name_tubing` AS `fe_bottom_id_tubing_out_name_tubing`,`exp_ec_expanded_old`.`fe_bottom_id_tubing_out_inner_diameter__mm` AS `fe_bottom_id_tubing_out_inner_diameter__mm`,`exp_ec_expanded_old`.`fe_bottom_id_tubing_out_color_code` AS `fe_bottom_id_tubing_out_color_code`,`exp_ec_expanded_old`.`fe_bottom_id_tubing_out_manufacturer` AS `fe_bottom_id_tubing_out_manufacturer`,`exp_ec_expanded_old`.`fe_bottom_id_tubing_out_model` AS `fe_bottom_id_tubing_out_model`,`exp_ec_expanded_old`.`fe_bottom_pump_rate_out__rpm` AS `fe_bottom_pump_rate_out__rpm`,`exp_ec_expanded_old`.`fe_bottom_flow_rate_real__mul_min` AS `fe_bottom_flow_rate_real__mul_min`,`exp_ec_expanded_old`.`fe_bottom_name_electrolyte` AS `fe_bottom_name_electrolyte`,`exp_ec_expanded_old`.`fe_bottom_c_electrolyte__mol_L` AS `fe_bottom_c_electrolyte__mol_L`,`exp_ec_expanded_old`.`fe_bottom_T_electrolyte__degC` AS `fe_bottom_T_electrolyte__degC`,`exp_ec_expanded_old`.`fg_top_Arring_name_gas` AS `fg_top_Arring_name_gas`,`exp_ec_expanded_old`.`fg_top_Arring_flow_rate__mL_min` AS `fg_top_Arring_flow_rate__mL_min`,`exp_ec_expanded_old`.`fg_top_purgevial_name_gas` AS `fg_top_purgevial_name_gas`,`exp_ec_expanded_old`.`fg_top_purgevial_flow_rate__mL_min` AS `fg_top_purgevial_flow_rate__mL_min`,`exp_ec_expanded_old`.`fg_top_main_name_gas` AS `fg_top_main_name_gas`,`exp_ec_expanded_old`.`fg_top_main_flow_rate__mL_min` AS `fg_top_main_flow_rate__mL_min`,`exp_ec_expanded_old`.`fg_bottom_Arring_name_gas` AS `fg_bottom_Arring_name_gas`,`exp_ec_expanded_old`.`fg_bottom_Arring_flow_rate__mL_min` AS `fg_bottom_Arring_flow_rate__mL_min`,`exp_ec_expanded_old`.`fg_bottom_purgevial_name_gas` AS `fg_bottom_purgevial_name_gas`,`exp_ec_expanded_old`.`fg_bottom_purgevial_flow_rate__mL_min` AS `fg_bottom_purgevial_flow_rate__mL_min`,`exp_ec_expanded_old`.`fg_bottom_main_name_gas` AS `fg_bottom_main_name_gas`,`exp_ec_expanded_old`.`fg_bottom_main_flow_rate__mL_min` AS `fg_bottom_main_flow_rate__mL_min` from (`exp_icpms_sfc_expanded` `ei` left join `exp_ec_expanded_old` on(((`exp_ec_expanded_old`.`t_start__timestamp` <= (`ei`.`t_start_delaycorrected__timestamp_sfc_pc` + interval `ei`.`t_duration__s` second)) and (`ei`.`t_start_delaycorrected__timestamp_sfc_pc` <= (`exp_ec_expanded_old`.`t_start__timestamp` + interval `exp_ec_expanded_old`.`t_duration__s` second)) and (`ei`.`name_setup_sfc` = `exp_ec_expanded_old`.`name_setup_sfc`))))) `exp_ec_expanded_old`) `exp_ec_expanded_old` on(((`dip`.`name_setup_sfc` = `exp_ec_expanded_old`.`name_setup_sfc`) and (`exp_ec_expanded_old`.`t_start__timestamp` <= `dip`.`t_delaycorrected__timestamp_sfc_pc`) and (((`exp_ec_expanded_old`.`t_start__timestamp` + interval `exp_ec_expanded_old`.`t_duration__s` second) + 5) >= `dip`.`t_delaycorrected__timestamp_sfc_pc`) and (`exp_ec_expanded_old`.`next_t_start_timestamp` >= `dip`.`t_delaycorrected__timestamp_sfc_pc`)))) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `data_icpms_sfc_batch_analysis`
--

/*!50001 DROP VIEW IF EXISTS `data_icpms_sfc_batch_analysis`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `data_icpms_sfc_batch_analysis` AS select `exp_icpms_sfc_batch_expanded`.`id_exp_icpms` AS `id_exp_icpms`,`exp_icpms_sfc_batch_expanded`.`name_isotope_analyte` AS `name_isotope_analyte`,`exp_icpms_sfc_batch_expanded`.`name_isotope_internalstandard` AS `name_isotope_internalstandard`,`dummy_data_icpms_sfc_batch_analysis`.`id_data_icpms` AS `id_data_icpms`,if((`dummy_data_icpms_sfc_batch_analysis`.`id_data_icpms` = 0),`exp_icpms_sfc_batch_expanded`.`t_start_delaycorrected__timestamp_sfc_pc`,`exp_icpms_sfc_batch_expanded`.`t_end_delaycorrected__timestamp_sfc_pc`) AS `t_delaycorrected__timestamp_sfc_pc`,`exp_icpms_sfc_batch_expanded`.`a_is__countratio` AS `a_is__countratio`,`exp_icpms_sfc_batch_expanded`.`c_a__mug_L` AS `c_a__mug_L`,`exp_icpms_sfc_batch_expanded`.`dm_dt__ng_s` AS `dm_dt__ng_s` from (`exp_icpms_sfc_batch_expanded` join `dummy_data_icpms_sfc_batch_analysis`) order by `exp_icpms_sfc_batch_expanded`.`id_exp_icpms`,`exp_icpms_sfc_batch_expanded`.`name_isotope_analyte`,`exp_icpms_sfc_batch_expanded`.`name_isotope_internalstandard`,`dummy_data_icpms_sfc_batch_analysis`.`id_data_icpms` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `data_stability_analysis`
--

/*!50001 DROP VIEW IF EXISTS `data_stability_analysis`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `data_stability_analysis` AS select `exp_icpms_integration_expanded`.`name_analysis` AS `name_analysis`,`exp_icpms_integration_expanded`.`id_exp_ec_dataset` AS `id_exp_ec_dataset`,`exp_icpms_integration_expanded`.`name_exp_ec_dataset` AS `name_exp_ec_dataset`,`exp_icpms_integration_expanded`.`name_user` AS `name_user`,`exp_icpms_integration_expanded`.`comment` AS `comment_icpms`,`exp_ec_integration_expanded`.`comment` AS `comment_ec`,`exp_icpms_integration_expanded`.`name_setup_sfc` AS `name_setup_sfc`,`exp_icpms_integration_expanded`.`element` AS `element`,`exp_icpms_integration_expanded`.`id_exp_icpms` AS `id_exp_icpms`,`exp_icpms_integration_expanded`.`name_isotope_analyte` AS `name_isotope_analyte`,`exp_icpms_integration_expanded`.`name_isotope_internalstandard` AS `name_isotope_internalstandard`,`exp_icpms_integration_expanded`.`id_ana_integration_icpms` AS `id_ana_integration_icpms`,`exp_icpms_integration_expanded`.`id_data_integration_icpms_baseline` AS `id_data_integration_icpms_baseline`,`exp_icpms_integration_expanded`.`id_data_integration_icpms_begin` AS `id_data_integration_icpms_begin`,`exp_icpms_integration_expanded`.`id_data_integration_icpms_end` AS `id_data_integration_icpms_end`,`exp_icpms_integration_expanded`.`t_integration_icpms_baseline__timestamp` AS `t_integration_icpms_baseline__timestamp`,`exp_icpms_integration_expanded`.`t_integration_icpms_begin__timestamp` AS `t_integration_icpms_begin__timestamp`,`exp_icpms_integration_expanded`.`t_integration_icpms_end__timestamp` AS `t_integration_icpms_end__timestamp`,`exp_icpms_integration_expanded`.`m_dissolved_simps__ng` AS `m_dissolved_simps__ng`,`exp_icpms_integration_expanded`.`m_dissolved_trapz__ng` AS `m_dissolved_trapz__ng`,`exp_icpms_integration_expanded`.`dm_dt_offset__ng_s` AS `dm_dt_offset__ng_s`,`exp_icpms_integration_expanded`.`no_of_datapoints_av_icpms` AS `no_of_datapoints_av_icpms`,`exp_icpms_integration_expanded`.`no_of_datapoints_rolling_icpms` AS `no_of_datapoints_rolling_icpms`,`exp_icpms_integration_expanded`.`auto_integration_icpms` AS `auto_integration_icpms`,`exp_icpms_integration_expanded`.`name_sample` AS `name_sample`,`exp_icpms_integration_expanded`.`name_setup_icpms` AS `name_setup_icpms`,`exp_icpms_integration_expanded`.`t_start__timestamp_icpms_pc` AS `t_start__timestamp_icpms_pc`,`exp_icpms_integration_expanded`.`t_duration__s` AS `t_duration__s`,`exp_icpms_integration_expanded`.`t_duration_planned__s` AS `t_duration_planned__s`,`exp_icpms_integration_expanded`.`type_experiment` AS `type_experiment`,`exp_icpms_integration_expanded`.`plasma_mode` AS `plasma_mode`,`exp_icpms_integration_expanded`.`tune_mode` AS `tune_mode`,`exp_icpms_integration_expanded`.`num_of_scans` AS `num_of_scans`,`exp_icpms_integration_expanded`.`id_exp_icpms_calibration_set` AS `id_exp_icpms_calibration_set`,`exp_icpms_integration_expanded`.`gas_dilution_factor` AS `gas_dilution_factor`,`exp_icpms_integration_expanded`.`name_gas_collision` AS `name_gas_collision`,`exp_icpms_integration_expanded`.`flow_rate_collision__mL_min` AS `flow_rate_collision__mL_min`,`exp_icpms_integration_expanded`.`name_gas_reaction` AS `name_gas_reaction`,`exp_icpms_integration_expanded`.`flow_rate_reaction__mL_min` AS `flow_rate_reaction__mL_min`,`exp_icpms_integration_expanded`.`name_computer_inserted_data` AS `name_computer_inserted_data`,`exp_icpms_integration_expanded`.`file_path_rawdata` AS `file_path_rawdata`,`exp_icpms_integration_expanded`.`t_inserted_data__timestamp` AS `t_inserted_data__timestamp`,`exp_icpms_integration_expanded`.`file_name_rawdata` AS `file_name_rawdata`,`exp_icpms_integration_expanded`.`t_start_delaycorrected__timestamp_sfc_pc` AS `t_start_delaycorrected__timestamp_sfc_pc`,`exp_icpms_integration_expanded`.`t_end_delaycorrected__timestamp_sfc_pc` AS `t_end_delaycorrected__timestamp_sfc_pc`,`exp_icpms_integration_expanded`.`t_start__timestamp_sfc_pc` AS `t_start__timestamp_sfc_pc`,`exp_icpms_integration_expanded`.`t_delay__s` AS `t_delay__s`,`exp_icpms_integration_expanded`.`flow_rate_real__mul_min` AS `flow_rate_real__mul_min`,`exp_icpms_integration_expanded`.`calibration_slope__countratio_mug_L` AS `calibration_slope__countratio_mug_L`,`exp_icpms_integration_expanded`.`delta_calibration_slope__countratio_mug_L` AS `delta_calibration_slope__countratio_mug_L`,`exp_icpms_integration_expanded`.`calibration_intercept__countratio` AS `calibration_intercept__countratio`,`exp_icpms_integration_expanded`.`delta_calibration_intercept__countratio` AS `delta_calibration_intercept__countratio`,`exp_icpms_integration_expanded`.`Rsquared` AS `Rsquared`,`exp_icpms_integration_expanded`.`calibration_method` AS `calibration_method`,`exp_icpms_integration_expanded`.`file_path_calibration_plot` AS `file_path_calibration_plot`,`exp_icpms_integration_expanded`.`name_computer_inserted_calibration_data` AS `name_computer_inserted_calibration_data`,`exp_icpms_integration_expanded`.`t_inserted_calibration_data__timestamp` AS `t_inserted_calibration_data__timestamp`,`exp_icpms_integration_expanded`.`name_isotope` AS `name_isotope`,`exp_icpms_integration_expanded`.`M__g_mol` AS `M__g_mol`,`exp_icpms_integration_expanded`.`n_dissolved_simps__mol` AS `n_dissolved_simps__mol`,`exp_icpms_integration_expanded`.`n_dissolved_trapz__mol` AS `n_dissolved_trapz__mol`,`exp_ec_integration_expanded`.`id_ana_integration_ec` AS `id_ana_integration_ec`,`exp_ec_integration_expanded`.`name_reaction` AS `name_reaction`,`exp_ec_integration_expanded`.`faradaic_efficiency__percent` AS `faradaic_efficiency__percent`,`exp_ec_integration_expanded`.`name_product_of_interest` AS `name_product_of_interest`,`exp_ec_integration_expanded`.`number_electrons` AS `number_electrons`,`exp_ec_integration_expanded`.`id_data_integration_ec_baseline` AS `id_data_integration_ec_baseline`,`exp_ec_integration_expanded`.`id_data_integration_ec_begin` AS `id_data_integration_ec_begin`,`exp_ec_integration_expanded`.`id_data_integration_ec_end` AS `id_data_integration_ec_end`,`exp_ec_integration_expanded`.`t_integration_ec_baseline__timestamp` AS `t_integration_ec_baseline__timestamp`,`exp_ec_integration_expanded`.`t_integration_ec_begin__timestamp` AS `t_integration_ec_begin__timestamp`,`exp_ec_integration_expanded`.`t_integration_ec_end__timestamp` AS `t_integration_ec_end__timestamp`,`exp_ec_integration_expanded`.`Q_integrated_simps__C` AS `Q_integrated_simps__C`,`exp_ec_integration_expanded`.`Q_integrated_trapz__C` AS `Q_integrated_trapz__C`,`exp_ec_integration_expanded`.`I_offset__A` AS `I_offset__A`,`exp_ec_integration_expanded`.`no_of_datapoints_av_ec` AS `no_of_datapoints_av_ec`,`exp_ec_integration_expanded`.`no_of_datapoints_rolling_ec` AS `no_of_datapoints_rolling_ec`,`exp_ec_integration_expanded`.`auto_integration_ec` AS `auto_integration_ec`,`exp_ec_integration_expanded`.`id_exp_sfc_first` AS `id_exp_sfc_first`,`exp_ec_integration_expanded`.`id_exp_sfc` AS `id_exp_sfc`,`exp_ec_integration_expanded`.`name_setup_sfc_alias` AS `name_setup_sfc_alias`,`exp_ec_integration_expanded`.`name_setup_sfc_feature` AS `name_setup_sfc_feature`,`exp_ec_integration_expanded`.`name_setup_sfc_type` AS `name_setup_sfc_type`,`exp_ec_integration_expanded`.`t_start__timestamp` AS `t_start__timestamp`,`exp_ec_integration_expanded`.`t_end__timestamp` AS `t_end__timestamp`,`exp_ec_integration_expanded`.`rawdata_path` AS `rawdata_path`,`exp_ec_integration_expanded`.`rawdata_computer` AS `rawdata_computer`,`exp_ec_integration_expanded`.`id_ML` AS `id_ML`,`exp_ec_integration_expanded`.`id_ML_technique` AS `id_ML_technique`,`exp_ec_integration_expanded`.`id_sample` AS `id_sample`,`exp_ec_integration_expanded`.`id_spot` AS `id_spot`,`exp_ec_integration_expanded`.`force__N` AS `force__N`,`exp_ec_integration_expanded`.`T_stage__degC` AS `T_stage__degC`,`exp_ec_integration_expanded`.`interrupted` AS `interrupted`,`exp_ec_integration_expanded`.`labview_sfc_version` AS `labview_sfc_version`,`exp_ec_integration_expanded`.`db_version` AS `db_version`,`exp_ec_integration_expanded`.`ec_name_technique` AS `ec_name_technique`,`exp_ec_integration_expanded`.`ec_R_u__ohm` AS `ec_R_u__ohm`,`exp_ec_integration_expanded`.`ec_iR_corr_in_situ__percent` AS `ec_iR_corr_in_situ__percent`,`exp_ec_integration_expanded`.`ec_R_u_determining_exp_ec` AS `ec_R_u_determining_exp_ec`,`exp_ec_integration_expanded`.`ec_E_RE__VvsRHE` AS `ec_E_RE__VvsRHE`,`exp_ec_integration_expanded`.`ec_name_RE` AS `ec_name_RE`,`exp_ec_integration_expanded`.`ec_name_RE_material` AS `ec_name_RE_material`,`exp_ec_integration_expanded`.`ec_name_RE_manufacturer` AS `ec_name_RE_manufacturer`,`exp_ec_integration_expanded`.`ec_name_RE_model` AS `ec_name_RE_model`,`exp_ec_integration_expanded`.`ec_name_CE` AS `ec_name_CE`,`exp_ec_integration_expanded`.`ec_name_CE_material` AS `ec_name_CE_material`,`exp_ec_integration_expanded`.`ec_name_CE_manufacturer` AS `ec_name_CE_manufacturer`,`exp_ec_integration_expanded`.`ec_name_CE_model` AS `ec_name_CE_model`,`exp_ec_integration_expanded`.`ec_name_device` AS `ec_name_device`,`exp_ec_integration_expanded`.`ec_id_control_mode` AS `ec_id_control_mode`,`exp_ec_integration_expanded`.`ec_id_ie_range` AS `ec_id_ie_range`,`exp_ec_integration_expanded`.`ec_id_vch_range` AS `ec_id_vch_range`,`exp_ec_integration_expanded`.`ec_id_ich_range` AS `ec_id_ich_range`,`exp_ec_integration_expanded`.`ec_id_vch_filter` AS `ec_id_vch_filter`,`exp_ec_integration_expanded`.`ec_id_ich_filter` AS `ec_id_ich_filter`,`exp_ec_integration_expanded`.`ec_id_ca_speed` AS `ec_id_ca_speed`,`exp_ec_integration_expanded`.`ec_id_ie_stability` AS `ec_id_ie_stability`,`exp_ec_integration_expanded`.`ec_id_sampling_mode` AS `ec_id_sampling_mode`,`exp_ec_integration_expanded`.`ec_ie_range_auto` AS `ec_ie_range_auto`,`exp_ec_integration_expanded`.`ec_vch_range_auto` AS `ec_vch_range_auto`,`exp_ec_integration_expanded`.`ec_ich_range_auto` AS `ec_ich_range_auto`,`exp_ec_integration_expanded`.`samples_id_sample` AS `samples_id_sample`,`exp_ec_integration_expanded`.`samples_name_sample` AS `samples_name_sample`,`exp_ec_integration_expanded`.`samples_name_user` AS `samples_name_user`,`exp_ec_integration_expanded`.`samples_t_manufactured__timestamp` AS `samples_t_manufactured__timestamp`,`exp_ec_integration_expanded`.`samples_comment` AS `samples_comment`,`exp_ec_integration_expanded`.`samples_total_loading__mg_cm2` AS `samples_total_loading__mg_cm2`,`exp_ec_integration_expanded`.`spots_id_spot` AS `spots_id_spot`,`exp_ec_integration_expanded`.`spots_spot_size__mm2` AS `spots_spot_size__mm2`,`exp_ec_integration_expanded`.`spots_pos_x__mm` AS `spots_pos_x__mm`,`exp_ec_integration_expanded`.`spots_pos_y__mm` AS `spots_pos_y__mm`,`exp_ec_integration_expanded`.`spots_comment` AS `spots_comment`,`exp_ec_integration_expanded`.`spots_total_loading__mg_cm2` AS `spots_total_loading__mg_cm2`,`exp_ec_integration_expanded`.`cv_E_initial__VvsRE` AS `cv_E_initial__VvsRE`,`exp_ec_integration_expanded`.`cv_E_apex1__VvsRE` AS `cv_E_apex1__VvsRE`,`exp_ec_integration_expanded`.`cv_E_apex2__VvsRE` AS `cv_E_apex2__VvsRE`,`exp_ec_integration_expanded`.`cv_E_final__VvsRE` AS `cv_E_final__VvsRE`,`exp_ec_integration_expanded`.`cv_scanrate__mV_s` AS `cv_scanrate__mV_s`,`exp_ec_integration_expanded`.`cv_stepsize__mV` AS `cv_stepsize__mV`,`exp_ec_integration_expanded`.`cv_cycles` AS `cv_cycles`,`exp_ec_integration_expanded`.`geis_f_initial__Hz` AS `geis_f_initial__Hz`,`exp_ec_integration_expanded`.`geis_f_final__Hz` AS `geis_f_final__Hz`,`exp_ec_integration_expanded`.`geis_I_dc__A` AS `geis_I_dc__A`,`exp_ec_integration_expanded`.`geis_I_amplitude__A` AS `geis_I_amplitude__A`,`exp_ec_integration_expanded`.`geis_R_initialguess__ohm` AS `geis_R_initialguess__ohm`,`exp_ec_integration_expanded`.`geis_points_per_decade` AS `geis_points_per_decade`,`exp_ec_integration_expanded`.`ghold_I_hold__A` AS `ghold_I_hold__A`,`exp_ec_integration_expanded`.`ghold_t_hold__s` AS `ghold_t_hold__s`,`exp_ec_integration_expanded`.`ghold_t_samplerate__s` AS `ghold_t_samplerate__s`,`exp_ec_integration_expanded`.`peis_f_initial__Hz` AS `peis_f_initial__Hz`,`exp_ec_integration_expanded`.`peis_f_final__Hz` AS `peis_f_final__Hz`,`exp_ec_integration_expanded`.`peis_E_dc__VvsRE` AS `peis_E_dc__VvsRE`,`exp_ec_integration_expanded`.`peis_E_amplitude__VvsRE` AS `peis_E_amplitude__VvsRE`,`exp_ec_integration_expanded`.`peis_R_initialguess__ohm` AS `peis_R_initialguess__ohm`,`exp_ec_integration_expanded`.`peis_points_per_decade` AS `peis_points_per_decade`,`exp_ec_integration_expanded`.`phold_E_hold__VvsRE` AS `phold_E_hold__VvsRE`,`exp_ec_integration_expanded`.`phold_t_hold__s` AS `phold_t_hold__s`,`exp_ec_integration_expanded`.`phold_t_samplerate__s` AS `phold_t_samplerate__s`,`exp_ec_integration_expanded`.`ppulse_E_hold1__VvsRE` AS `ppulse_E_hold1__VvsRE`,`exp_ec_integration_expanded`.`ppulse_E_hold2__VvsRE` AS `ppulse_E_hold2__VvsRE`,`exp_ec_integration_expanded`.`ppulse_t_hold1__s` AS `ppulse_t_hold1__s`,`exp_ec_integration_expanded`.`ppulse_t_hold2__s` AS `ppulse_t_hold2__s`,`exp_ec_integration_expanded`.`ppulse_t_samplerate__s` AS `ppulse_t_samplerate__s`,`exp_ec_integration_expanded`.`ppulse_cycles` AS `ppulse_cycles`,`exp_ec_integration_expanded`.`gpulse_I_hold1__A` AS `gpulse_I_hold1__A`,`exp_ec_integration_expanded`.`gpulse_I_hold2__A` AS `gpulse_I_hold2__A`,`exp_ec_integration_expanded`.`gpulse_t_hold1__s` AS `gpulse_t_hold1__s`,`exp_ec_integration_expanded`.`gpulse_t_hold2__s` AS `gpulse_t_hold2__s`,`exp_ec_integration_expanded`.`gpulse_t_samplerate__s` AS `gpulse_t_samplerate__s`,`exp_ec_integration_expanded`.`gpulse_cycles` AS `gpulse_cycles`,`exp_ec_integration_expanded`.`ramp_E_initial__VvsRE` AS `ramp_E_initial__VvsRE`,`exp_ec_integration_expanded`.`ramp_E_final__VvsRE` AS `ramp_E_final__VvsRE`,`exp_ec_integration_expanded`.`ramp_scanrate__mV_s` AS `ramp_scanrate__mV_s`,`exp_ec_integration_expanded`.`ramp_stepsize__mV` AS `ramp_stepsize__mV`,`exp_ec_integration_expanded`.`ramp_cycles` AS `ramp_cycles`,`exp_ec_integration_expanded`.`fc_top_name_flow_cell` AS `fc_top_name_flow_cell`,`exp_ec_integration_expanded`.`fc_top_name_flow_cell_name_user` AS `fc_top_name_flow_cell_name_user`,`exp_ec_integration_expanded`.`fc_top_name_flow_cell_material` AS `fc_top_name_flow_cell_material`,`exp_ec_integration_expanded`.`fc_top_name_flow_cell_A_opening_ideal__mm2` AS `fc_top_name_flow_cell_A_opening_ideal__mm2`,`exp_ec_integration_expanded`.`fc_top_name_flow_cell_A_opening_real__mm2` AS `fc_top_name_flow_cell_A_opening_real__mm2`,`exp_ec_integration_expanded`.`fc_top_name_flow_cell_manufacture_date` AS `fc_top_name_flow_cell_manufacture_date`,`exp_ec_integration_expanded`.`fc_top_name_flow_cell_CAD_file` AS `fc_top_name_flow_cell_CAD_file`,`exp_ec_integration_expanded`.`fc_top_name_flow_cell_comment` AS `fc_top_name_flow_cell_comment`,`exp_ec_integration_expanded`.`fc_top_id_sealing` AS `fc_top_id_sealing`,`exp_ec_integration_expanded`.`fc_top_id_sealing_name_user` AS `fc_top_id_sealing_name_user`,`exp_ec_integration_expanded`.`fc_top_id_sealing_material` AS `fc_top_id_sealing_material`,`exp_ec_integration_expanded`.`fc_top_id_sealing_A_sealing__mm2` AS `fc_top_id_sealing_A_sealing__mm2`,`exp_ec_integration_expanded`.`fc_top_id_sealing_A_opening__mm2` AS `fc_top_id_sealing_A_opening__mm2`,`exp_ec_integration_expanded`.`fc_top_id_sealing_thickness__mm` AS `fc_top_id_sealing_thickness__mm`,`exp_ec_integration_expanded`.`fc_top_id_sealing_shaping_method` AS `fc_top_id_sealing_shaping_method`,`exp_ec_integration_expanded`.`fc_top_id_sealing_comment` AS `fc_top_id_sealing_comment`,`exp_ec_integration_expanded`.`fc_top_id_PTL` AS `fc_top_id_PTL`,`exp_ec_integration_expanded`.`fc_top_id_PTL_name_user` AS `fc_top_id_PTL_name_user`,`exp_ec_integration_expanded`.`fc_top_id_PTL_material` AS `fc_top_id_PTL_material`,`exp_ec_integration_expanded`.`fc_top_id_PTL_thickness__mm` AS `fc_top_id_PTL_thickness__mm`,`exp_ec_integration_expanded`.`fc_top_id_PTL_manufacturer` AS `fc_top_id_PTL_manufacturer`,`exp_ec_integration_expanded`.`fc_top_id_PTL_A_PTL__mm2` AS `fc_top_id_PTL_A_PTL__mm2`,`exp_ec_integration_expanded`.`fc_top_id_PTL_shaping_method` AS `fc_top_id_PTL_shaping_method`,`exp_ec_integration_expanded`.`fc_top_id_PTL_comment` AS `fc_top_id_PTL_comment`,`exp_ec_integration_expanded`.`fc_bottom_name_flow_cell` AS `fc_bottom_name_flow_cell`,`exp_ec_integration_expanded`.`fc_bottom_name_flow_cell_name_user` AS `fc_bottom_name_flow_cell_name_user`,`exp_ec_integration_expanded`.`fc_bottom_name_flow_cell_material` AS `fc_bottom_name_flow_cell_material`,`exp_ec_integration_expanded`.`fc_bottom_name_flow_cell_A_opening_ideal__mm2` AS `fc_bottom_name_flow_cell_A_opening_ideal__mm2`,`exp_ec_integration_expanded`.`fc_bottom_name_flow_cell_A_opening_real__mm2` AS `fc_bottom_name_flow_cell_A_opening_real__mm2`,`exp_ec_integration_expanded`.`fc_bottom_name_flow_cell_manufacture_date` AS `fc_bottom_name_flow_cell_manufacture_date`,`exp_ec_integration_expanded`.`fc_bottom_name_flow_cell_CAD_file` AS `fc_bottom_name_flow_cell_CAD_file`,`exp_ec_integration_expanded`.`fc_bottom_name_flow_cell_comment` AS `fc_bottom_name_flow_cell_comment`,`exp_ec_integration_expanded`.`fc_bottom_id_sealing` AS `fc_bottom_id_sealing`,`exp_ec_integration_expanded`.`fc_bottom_id_sealing_name_user` AS `fc_bottom_id_sealing_name_user`,`exp_ec_integration_expanded`.`fc_bottom_id_sealing_material` AS `fc_bottom_id_sealing_material`,`exp_ec_integration_expanded`.`fc_bottom_id_sealing_A_sealing__mm2` AS `fc_bottom_id_sealing_A_sealing__mm2`,`exp_ec_integration_expanded`.`fc_bottom_id_sealing_A_opening__mm2` AS `fc_bottom_id_sealing_A_opening__mm2`,`exp_ec_integration_expanded`.`fc_bottom_id_sealing_thickness__mm` AS `fc_bottom_id_sealing_thickness__mm`,`exp_ec_integration_expanded`.`fc_bottom_id_sealing_shaping_method` AS `fc_bottom_id_sealing_shaping_method`,`exp_ec_integration_expanded`.`fc_bottom_id_sealing_comment` AS `fc_bottom_id_sealing_comment`,`exp_ec_integration_expanded`.`fc_bottom_id_PTL` AS `fc_bottom_id_PTL`,`exp_ec_integration_expanded`.`fc_bottom_id_PTL_name_user` AS `fc_bottom_id_PTL_name_user`,`exp_ec_integration_expanded`.`fc_bottom_id_PTL_material` AS `fc_bottom_id_PTL_material`,`exp_ec_integration_expanded`.`fc_bottom_id_PTL_thickness__mm` AS `fc_bottom_id_PTL_thickness__mm`,`exp_ec_integration_expanded`.`fc_bottom_id_PTL_manufacturer` AS `fc_bottom_id_PTL_manufacturer`,`exp_ec_integration_expanded`.`fc_bottom_id_PTL_A_PTL__mm2` AS `fc_bottom_id_PTL_A_PTL__mm2`,`exp_ec_integration_expanded`.`fc_bottom_id_PTL_shaping_method` AS `fc_bottom_id_PTL_shaping_method`,`exp_ec_integration_expanded`.`fc_bottom_id_PTL_comment` AS `fc_bottom_id_PTL_comment`,`exp_ec_integration_expanded`.`fe_top_id_pump_in` AS `fe_top_id_pump_in`,`exp_ec_integration_expanded`.`fe_top_id_pump_in_manufacturer` AS `fe_top_id_pump_in_manufacturer`,`exp_ec_integration_expanded`.`fe_top_id_pump_in_model` AS `fe_top_id_pump_in_model`,`exp_ec_integration_expanded`.`fe_top_id_pump_in_device` AS `fe_top_id_pump_in_device`,`exp_ec_integration_expanded`.`fe_top_id_tubing_in` AS `fe_top_id_tubing_in`,`exp_ec_integration_expanded`.`fe_top_id_tubing_in_name_tubing` AS `fe_top_id_tubing_in_name_tubing`,`exp_ec_integration_expanded`.`fe_top_id_tubing_in_inner_diameter__mm` AS `fe_top_id_tubing_in_inner_diameter__mm`,`exp_ec_integration_expanded`.`fe_top_id_tubing_in_color_code` AS `fe_top_id_tubing_in_color_code`,`exp_ec_integration_expanded`.`fe_top_id_tubing_in_manufacturer` AS `fe_top_id_tubing_in_manufacturer`,`exp_ec_integration_expanded`.`fe_top_id_tubing_in_model` AS `fe_top_id_tubing_in_model`,`exp_ec_integration_expanded`.`fe_top_pump_rate_in__rpm` AS `fe_top_pump_rate_in__rpm`,`exp_ec_integration_expanded`.`fe_top_id_pump_out` AS `fe_top_id_pump_out`,`exp_ec_integration_expanded`.`fe_top_id_pump_out_manufacturer` AS `fe_top_id_pump_out_manufacturer`,`exp_ec_integration_expanded`.`fe_top_id_pump_out_model` AS `fe_top_id_pump_out_model`,`exp_ec_integration_expanded`.`fe_top_id_pump_out_device` AS `fe_top_id_pump_out_device`,`exp_ec_integration_expanded`.`fe_top_id_tubing_out` AS `fe_top_id_tubing_out`,`exp_ec_integration_expanded`.`fe_top_id_tubing_out_name_tubing` AS `fe_top_id_tubing_out_name_tubing`,`exp_ec_integration_expanded`.`fe_top_id_tubing_out_inner_diameter__mm` AS `fe_top_id_tubing_out_inner_diameter__mm`,`exp_ec_integration_expanded`.`fe_top_id_tubing_out_color_code` AS `fe_top_id_tubing_out_color_code`,`exp_ec_integration_expanded`.`fe_top_id_tubing_out_manufacturer` AS `fe_top_id_tubing_out_manufacturer`,`exp_ec_integration_expanded`.`fe_top_id_tubing_out_model` AS `fe_top_id_tubing_out_model`,`exp_ec_integration_expanded`.`fe_top_pump_rate_out__rpm` AS `fe_top_pump_rate_out__rpm`,`exp_ec_integration_expanded`.`fe_top_flow_rate_real__mul_min` AS `fe_top_flow_rate_real__mul_min`,`exp_ec_integration_expanded`.`fe_top_name_electrolyte` AS `fe_top_name_electrolyte`,`exp_ec_integration_expanded`.`fe_top_c_electrolyte__mol_L` AS `fe_top_c_electrolyte__mol_L`,`exp_ec_integration_expanded`.`fe_top_T_electrolyte__degC` AS `fe_top_T_electrolyte__degC`,`exp_ec_integration_expanded`.`fe_bottom_id_pump_in` AS `fe_bottom_id_pump_in`,`exp_ec_integration_expanded`.`fe_bottom_id_pump_in_manufacturer` AS `fe_bottom_id_pump_in_manufacturer`,`exp_ec_integration_expanded`.`fe_bottom_id_pump_in_model` AS `fe_bottom_id_pump_in_model`,`exp_ec_integration_expanded`.`fe_bottom_id_pump_in_device` AS `fe_bottom_id_pump_in_device`,`exp_ec_integration_expanded`.`fe_bottom_id_tubing_in` AS `fe_bottom_id_tubing_in`,`exp_ec_integration_expanded`.`fe_bottom_id_tubing_in_name_tubing` AS `fe_bottom_id_tubing_in_name_tubing`,`exp_ec_integration_expanded`.`fe_bottom_id_tubing_in_inner_diameter__mm` AS `fe_bottom_id_tubing_in_inner_diameter__mm`,`exp_ec_integration_expanded`.`fe_bottom_id_tubing_in_color_code` AS `fe_bottom_id_tubing_in_color_code`,`exp_ec_integration_expanded`.`fe_bottom_id_tubing_in_manufacturer` AS `fe_bottom_id_tubing_in_manufacturer`,`exp_ec_integration_expanded`.`fe_bottom_id_tubing_in_model` AS `fe_bottom_id_tubing_in_model`,`exp_ec_integration_expanded`.`fe_bottom_pump_rate_in__rpm` AS `fe_bottom_pump_rate_in__rpm`,`exp_ec_integration_expanded`.`fe_bottom_id_pump_out` AS `fe_bottom_id_pump_out`,`exp_ec_integration_expanded`.`fe_bottom_id_pump_out_manufacturer` AS `fe_bottom_id_pump_out_manufacturer`,`exp_ec_integration_expanded`.`fe_bottom_id_pump_out_model` AS `fe_bottom_id_pump_out_model`,`exp_ec_integration_expanded`.`fe_bottom_id_pump_out_device` AS `fe_bottom_id_pump_out_device`,`exp_ec_integration_expanded`.`fe_bottom_id_tubing_out` AS `fe_bottom_id_tubing_out`,`exp_ec_integration_expanded`.`fe_bottom_id_tubing_out_name_tubing` AS `fe_bottom_id_tubing_out_name_tubing`,`exp_ec_integration_expanded`.`fe_bottom_id_tubing_out_inner_diameter__mm` AS `fe_bottom_id_tubing_out_inner_diameter__mm`,`exp_ec_integration_expanded`.`fe_bottom_id_tubing_out_color_code` AS `fe_bottom_id_tubing_out_color_code`,`exp_ec_integration_expanded`.`fe_bottom_id_tubing_out_manufacturer` AS `fe_bottom_id_tubing_out_manufacturer`,`exp_ec_integration_expanded`.`fe_bottom_id_tubing_out_model` AS `fe_bottom_id_tubing_out_model`,`exp_ec_integration_expanded`.`fe_bottom_pump_rate_out__rpm` AS `fe_bottom_pump_rate_out__rpm`,`exp_ec_integration_expanded`.`fe_bottom_flow_rate_real__mul_min` AS `fe_bottom_flow_rate_real__mul_min`,`exp_ec_integration_expanded`.`fe_bottom_name_electrolyte` AS `fe_bottom_name_electrolyte`,`exp_ec_integration_expanded`.`fe_bottom_c_electrolyte__mol_L` AS `fe_bottom_c_electrolyte__mol_L`,`exp_ec_integration_expanded`.`fe_bottom_T_electrolyte__degC` AS `fe_bottom_T_electrolyte__degC`,`exp_ec_integration_expanded`.`fg_top_Arring_name_gas` AS `fg_top_Arring_name_gas`,`exp_ec_integration_expanded`.`fg_top_Arring_flow_rate__mL_min` AS `fg_top_Arring_flow_rate__mL_min`,`exp_ec_integration_expanded`.`fg_top_purgevial_name_gas` AS `fg_top_purgevial_name_gas`,`exp_ec_integration_expanded`.`fg_top_purgevial_flow_rate__mL_min` AS `fg_top_purgevial_flow_rate__mL_min`,`exp_ec_integration_expanded`.`fg_top_main_name_gas` AS `fg_top_main_name_gas`,`exp_ec_integration_expanded`.`fg_top_main_flow_rate__mL_min` AS `fg_top_main_flow_rate__mL_min`,`exp_ec_integration_expanded`.`fg_bottom_Arring_name_gas` AS `fg_bottom_Arring_name_gas`,`exp_ec_integration_expanded`.`fg_bottom_Arring_flow_rate__mL_min` AS `fg_bottom_Arring_flow_rate__mL_min`,`exp_ec_integration_expanded`.`fg_bottom_purgevial_name_gas` AS `fg_bottom_purgevial_name_gas`,`exp_ec_integration_expanded`.`fg_bottom_purgevial_flow_rate__mL_min` AS `fg_bottom_purgevial_flow_rate__mL_min`,`exp_ec_integration_expanded`.`fg_bottom_main_name_gas` AS `fg_bottom_main_name_gas`,`exp_ec_integration_expanded`.`fg_bottom_main_flow_rate__mL_min` AS `fg_bottom_main_flow_rate__mL_min`,if((`exp_ec_integration_expanded`.`fe_top_id_pump_out_device` = 'ICP-MS'),'top',if((`exp_ec_integration_expanded`.`fe_bottom_id_pump_out_device` = 'ICP-MS'),'bottom',NULL)) AS `location`,`exp_ec_integration_expanded`.`n_product_of_interest_simps__mol` AS `n_product_of_interest_simps__mol`,`exp_ec_integration_expanded`.`n_product_of_interest_trapz__mol` AS `n_product_of_interest_trapz__mol`,(`exp_ec_integration_expanded`.`n_product_of_interest_simps__mol` / `exp_icpms_integration_expanded`.`n_dissolved_simps__mol`) AS `S_number_simps`,(`exp_ec_integration_expanded`.`n_product_of_interest_trapz__mol` / `exp_icpms_integration_expanded`.`n_dissolved_trapz__mol`) AS `S_number_trapz` from (`exp_icpms_integration_expanded` left join `exp_ec_integration_expanded` on(((`exp_icpms_integration_expanded`.`name_analysis` = `exp_ec_integration_expanded`.`name_analysis`) and (`exp_icpms_integration_expanded`.`id_exp_ec_dataset` = `exp_ec_integration_expanded`.`id_exp_ec_dataset`) and (`exp_icpms_integration_expanded`.`name_user` = `exp_ec_integration_expanded`.`name_user`) and (`exp_icpms_integration_expanded`.`name_setup_sfc` = `exp_ec_integration_expanded`.`name_setup_sfc`)))) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `data_stability_batch_analysis`
--

/*!50001 DROP VIEW IF EXISTS `data_stability_batch_analysis`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `data_stability_batch_analysis` AS select `exp_icpms_sfc_batch_expanded`.`id_exp_icpms` AS `id_exp_icpms`,`exp_icpms_sfc_batch_expanded`.`name_isotope_analyte` AS `name_isotope_analyte`,`exp_icpms_sfc_batch_expanded`.`name_isotope_internalstandard` AS `name_isotope_internalstandard`,`exp_icpms_sfc_batch_expanded`.`name_analysis` AS `name_analysis`,`exp_icpms_sfc_batch_expanded`.`id_exp_ec_dataset` AS `id_exp_ec_dataset`,`exp_icpms_sfc_batch_expanded`.`name_exp_ec_dataset` AS `name_exp_ec_dataset`,`exp_icpms_sfc_batch_expanded`.`id_exp_icpms_sfc_online` AS `id_exp_icpms_sfc_online`,`exp_icpms_sfc_batch_expanded`.`id_exp_icpms_calibration_set` AS `id_exp_icpms_calibration_set`,`exp_icpms_sfc_batch_expanded`.`name_setup_sfc` AS `name_setup_sfc`,`exp_icpms_sfc_batch_expanded`.`location` AS `location`,`exp_icpms_sfc_batch_expanded`.`t_delay__s` AS `t_delay__s`,`exp_icpms_sfc_batch_expanded`.`t_start__timestamp_sfc_pc` AS `t_start__timestamp_sfc_pc`,`exp_icpms_sfc_batch_expanded`.`t_end__timestamp_sfc_pc` AS `t_end__timestamp_sfc_pc`,`exp_icpms_sfc_batch_expanded`.`t_start_delaycorrected__timestamp_sfc_pc` AS `t_start_delaycorrected__timestamp_sfc_pc`,`exp_icpms_sfc_batch_expanded`.`t_end_delaycorrected__timestamp_sfc_pc` AS `t_end_delaycorrected__timestamp_sfc_pc`,`exp_icpms_sfc_batch_expanded`.`m_start__g` AS `m_start__g`,`exp_icpms_sfc_batch_expanded`.`m_end__g` AS `m_end__g`,`exp_icpms_sfc_batch_expanded`.`density__g_mL` AS `density__g_mL`,`exp_icpms_sfc_batch_expanded`.`comment` AS `comment`,`exp_icpms_sfc_batch_expanded`.`name_sample` AS `name_sample`,`exp_icpms_sfc_batch_expanded`.`name_user` AS `name_user`,`exp_icpms_sfc_batch_expanded`.`name_setup_icpms` AS `name_setup_icpms`,`exp_icpms_sfc_batch_expanded`.`t_start__timestamp_icpms_pc` AS `t_start__timestamp_icpms_pc`,`exp_icpms_sfc_batch_expanded`.`t_duration__s` AS `t_duration__s`,`exp_icpms_sfc_batch_expanded`.`t_duration_planned__s` AS `t_duration_planned__s`,`exp_icpms_sfc_batch_expanded`.`type_experiment` AS `type_experiment`,`exp_icpms_sfc_batch_expanded`.`plasma_mode` AS `plasma_mode`,`exp_icpms_sfc_batch_expanded`.`tune_mode` AS `tune_mode`,`exp_icpms_sfc_batch_expanded`.`num_of_scans` AS `num_of_scans`,`exp_icpms_sfc_batch_expanded`.`gas_dilution_factor` AS `gas_dilution_factor`,`exp_icpms_sfc_batch_expanded`.`name_gas_collision` AS `name_gas_collision`,`exp_icpms_sfc_batch_expanded`.`flow_rate_collision__mL_min` AS `flow_rate_collision__mL_min`,`exp_icpms_sfc_batch_expanded`.`name_gas_reaction` AS `name_gas_reaction`,`exp_icpms_sfc_batch_expanded`.`flow_rate_reaction__mL_min` AS `flow_rate_reaction__mL_min`,`exp_icpms_sfc_batch_expanded`.`name_computer_inserted_data` AS `name_computer_inserted_data`,`exp_icpms_sfc_batch_expanded`.`file_path_rawdata` AS `file_path_rawdata`,`exp_icpms_sfc_batch_expanded`.`t_inserted_data__timestamp` AS `t_inserted_data__timestamp`,`exp_icpms_sfc_batch_expanded`.`file_name_rawdata` AS `file_name_rawdata`,`exp_icpms_sfc_batch_expanded`.`c_analyte__mug_L` AS `c_analyte__mug_L`,`exp_icpms_sfc_batch_expanded`.`c_internalstandard__mug_L` AS `c_internalstandard__mug_L`,`exp_icpms_sfc_batch_expanded`.`t_integration_analyte__s` AS `t_integration_analyte__s`,`exp_icpms_sfc_batch_expanded`.`t_integration_internalstandard__s` AS `t_integration_internalstandard__s`,`exp_icpms_sfc_batch_expanded`.`a_is__countratio` AS `a_is__countratio`,`exp_icpms_sfc_batch_expanded`.`a_is_std__countratio` AS `a_is_std__countratio`,`exp_icpms_sfc_batch_expanded`.`calibration_slope__countratio_mug_L` AS `calibration_slope__countratio_mug_L`,`exp_icpms_sfc_batch_expanded`.`delta_calibration_slope__countratio_mug_L` AS `delta_calibration_slope__countratio_mug_L`,`exp_icpms_sfc_batch_expanded`.`calibration_intercept__countratio` AS `calibration_intercept__countratio`,`exp_icpms_sfc_batch_expanded`.`delta_calibration_intercept__countratio` AS `delta_calibration_intercept__countratio`,`exp_icpms_sfc_batch_expanded`.`Rsquared` AS `Rsquared`,`exp_icpms_sfc_batch_expanded`.`calibration_method` AS `calibration_method`,`exp_icpms_sfc_batch_expanded`.`file_path_calibration_plot` AS `file_path_calibration_plot`,`exp_icpms_sfc_batch_expanded`.`name_computer_inserted_calibration_data` AS `name_computer_inserted_calibration_data`,`exp_icpms_sfc_batch_expanded`.`t_inserted_calibration_data__timestamp` AS `t_inserted_calibration_data__timestamp`,`exp_icpms_sfc_batch_expanded`.`Delta_t__s` AS `Delta_t__s`,`exp_icpms_sfc_batch_expanded`.`flow_rate_real__mul_min` AS `flow_rate_real__mul_min`,`exp_icpms_sfc_batch_expanded`.`c_a__mug_L` AS `c_a__mug_L`,`exp_icpms_sfc_batch_expanded`.`dm_dt__ng_s` AS `dm_dt__ng_s`,`exp_icpms_sfc_batch_expanded`.`m_batch__ng` AS `m_batch__ng`,`exp_icpms_sfc_batch_expanded`.`n_batch__mol` AS `n_batch__mol`,`exp_ec_integration_expanded`.`id_ana_integration_ec` AS `id_ana_integration_ec`,`exp_ec_integration_expanded`.`name_reaction` AS `name_reaction`,`exp_ec_integration_expanded`.`faradaic_efficiency__percent` AS `faradaic_efficiency__percent`,`exp_ec_integration_expanded`.`name_product_of_interest` AS `name_product_of_interest`,`exp_ec_integration_expanded`.`number_electrons` AS `number_electrons`,`exp_ec_integration_expanded`.`id_data_integration_ec_baseline` AS `id_data_integration_ec_baseline`,`exp_ec_integration_expanded`.`id_data_integration_ec_begin` AS `id_data_integration_ec_begin`,`exp_ec_integration_expanded`.`id_data_integration_ec_end` AS `id_data_integration_ec_end`,`exp_ec_integration_expanded`.`t_integration_ec_baseline__timestamp` AS `t_integration_ec_baseline__timestamp`,`exp_ec_integration_expanded`.`t_integration_ec_begin__timestamp` AS `t_integration_ec_begin__timestamp`,`exp_ec_integration_expanded`.`t_integration_ec_end__timestamp` AS `t_integration_ec_end__timestamp`,`exp_ec_integration_expanded`.`Q_integrated_simps__C` AS `Q_integrated_simps__C`,`exp_ec_integration_expanded`.`Q_integrated_trapz__C` AS `Q_integrated_trapz__C`,`exp_ec_integration_expanded`.`I_offset__A` AS `I_offset__A`,`exp_ec_integration_expanded`.`no_of_datapoints_av_ec` AS `no_of_datapoints_av_ec`,`exp_ec_integration_expanded`.`no_of_datapoints_rolling_ec` AS `no_of_datapoints_rolling_ec`,`exp_ec_integration_expanded`.`auto_integration_ec` AS `auto_integration_ec`,`exp_ec_integration_expanded`.`id_exp_sfc_first` AS `id_exp_sfc_first`,`exp_ec_integration_expanded`.`id_exp_sfc` AS `id_exp_sfc`,`exp_ec_integration_expanded`.`name_setup_sfc_alias` AS `name_setup_sfc_alias`,`exp_ec_integration_expanded`.`name_setup_sfc_feature` AS `name_setup_sfc_feature`,`exp_ec_integration_expanded`.`name_setup_sfc_type` AS `name_setup_sfc_type`,`exp_ec_integration_expanded`.`t_start__timestamp` AS `t_start__timestamp`,`exp_ec_integration_expanded`.`t_end__timestamp` AS `t_end__timestamp`,`exp_ec_integration_expanded`.`rawdata_path` AS `rawdata_path`,`exp_ec_integration_expanded`.`rawdata_computer` AS `rawdata_computer`,`exp_ec_integration_expanded`.`id_ML` AS `id_ML`,`exp_ec_integration_expanded`.`id_ML_technique` AS `id_ML_technique`,`exp_ec_integration_expanded`.`id_sample` AS `id_sample`,`exp_ec_integration_expanded`.`id_spot` AS `id_spot`,`exp_ec_integration_expanded`.`force__N` AS `force__N`,`exp_ec_integration_expanded`.`T_stage__degC` AS `T_stage__degC`,`exp_ec_integration_expanded`.`interrupted` AS `interrupted`,`exp_ec_integration_expanded`.`labview_sfc_version` AS `labview_sfc_version`,`exp_ec_integration_expanded`.`db_version` AS `db_version`,`exp_ec_integration_expanded`.`ec_name_technique` AS `ec_name_technique`,`exp_ec_integration_expanded`.`ec_R_u__ohm` AS `ec_R_u__ohm`,`exp_ec_integration_expanded`.`ec_iR_corr_in_situ__percent` AS `ec_iR_corr_in_situ__percent`,`exp_ec_integration_expanded`.`ec_R_u_determining_exp_ec` AS `ec_R_u_determining_exp_ec`,`exp_ec_integration_expanded`.`ec_E_RE__VvsRHE` AS `ec_E_RE__VvsRHE`,`exp_ec_integration_expanded`.`ec_name_RE` AS `ec_name_RE`,`exp_ec_integration_expanded`.`ec_name_RE_material` AS `ec_name_RE_material`,`exp_ec_integration_expanded`.`ec_name_RE_manufacturer` AS `ec_name_RE_manufacturer`,`exp_ec_integration_expanded`.`ec_name_RE_model` AS `ec_name_RE_model`,`exp_ec_integration_expanded`.`ec_name_CE` AS `ec_name_CE`,`exp_ec_integration_expanded`.`ec_name_CE_material` AS `ec_name_CE_material`,`exp_ec_integration_expanded`.`ec_name_CE_manufacturer` AS `ec_name_CE_manufacturer`,`exp_ec_integration_expanded`.`ec_name_CE_model` AS `ec_name_CE_model`,`exp_ec_integration_expanded`.`ec_name_device` AS `ec_name_device`,`exp_ec_integration_expanded`.`ec_id_control_mode` AS `ec_id_control_mode`,`exp_ec_integration_expanded`.`ec_id_ie_range` AS `ec_id_ie_range`,`exp_ec_integration_expanded`.`ec_id_vch_range` AS `ec_id_vch_range`,`exp_ec_integration_expanded`.`ec_id_ich_range` AS `ec_id_ich_range`,`exp_ec_integration_expanded`.`ec_id_vch_filter` AS `ec_id_vch_filter`,`exp_ec_integration_expanded`.`ec_id_ich_filter` AS `ec_id_ich_filter`,`exp_ec_integration_expanded`.`ec_id_ca_speed` AS `ec_id_ca_speed`,`exp_ec_integration_expanded`.`ec_id_ie_stability` AS `ec_id_ie_stability`,`exp_ec_integration_expanded`.`ec_id_sampling_mode` AS `ec_id_sampling_mode`,`exp_ec_integration_expanded`.`ec_ie_range_auto` AS `ec_ie_range_auto`,`exp_ec_integration_expanded`.`ec_vch_range_auto` AS `ec_vch_range_auto`,`exp_ec_integration_expanded`.`ec_ich_range_auto` AS `ec_ich_range_auto`,`exp_ec_integration_expanded`.`samples_id_sample` AS `samples_id_sample`,`exp_ec_integration_expanded`.`samples_name_sample` AS `samples_name_sample`,`exp_ec_integration_expanded`.`samples_name_user` AS `samples_name_user`,`exp_ec_integration_expanded`.`samples_t_manufactured__timestamp` AS `samples_t_manufactured__timestamp`,`exp_ec_integration_expanded`.`samples_comment` AS `samples_comment`,`exp_ec_integration_expanded`.`samples_total_loading__mg_cm2` AS `samples_total_loading__mg_cm2`,`exp_ec_integration_expanded`.`spots_id_spot` AS `spots_id_spot`,`exp_ec_integration_expanded`.`spots_spot_size__mm2` AS `spots_spot_size__mm2`,`exp_ec_integration_expanded`.`spots_pos_x__mm` AS `spots_pos_x__mm`,`exp_ec_integration_expanded`.`spots_pos_y__mm` AS `spots_pos_y__mm`,`exp_ec_integration_expanded`.`spots_comment` AS `spots_comment`,`exp_ec_integration_expanded`.`spots_total_loading__mg_cm2` AS `spots_total_loading__mg_cm2`,`exp_ec_integration_expanded`.`cv_E_initial__VvsRE` AS `cv_E_initial__VvsRE`,`exp_ec_integration_expanded`.`cv_E_apex1__VvsRE` AS `cv_E_apex1__VvsRE`,`exp_ec_integration_expanded`.`cv_E_apex2__VvsRE` AS `cv_E_apex2__VvsRE`,`exp_ec_integration_expanded`.`cv_E_final__VvsRE` AS `cv_E_final__VvsRE`,`exp_ec_integration_expanded`.`cv_scanrate__mV_s` AS `cv_scanrate__mV_s`,`exp_ec_integration_expanded`.`cv_stepsize__mV` AS `cv_stepsize__mV`,`exp_ec_integration_expanded`.`cv_cycles` AS `cv_cycles`,`exp_ec_integration_expanded`.`geis_f_initial__Hz` AS `geis_f_initial__Hz`,`exp_ec_integration_expanded`.`geis_f_final__Hz` AS `geis_f_final__Hz`,`exp_ec_integration_expanded`.`geis_I_dc__A` AS `geis_I_dc__A`,`exp_ec_integration_expanded`.`geis_I_amplitude__A` AS `geis_I_amplitude__A`,`exp_ec_integration_expanded`.`geis_R_initialguess__ohm` AS `geis_R_initialguess__ohm`,`exp_ec_integration_expanded`.`geis_points_per_decade` AS `geis_points_per_decade`,`exp_ec_integration_expanded`.`ghold_I_hold__A` AS `ghold_I_hold__A`,`exp_ec_integration_expanded`.`ghold_t_hold__s` AS `ghold_t_hold__s`,`exp_ec_integration_expanded`.`ghold_t_samplerate__s` AS `ghold_t_samplerate__s`,`exp_ec_integration_expanded`.`peis_f_initial__Hz` AS `peis_f_initial__Hz`,`exp_ec_integration_expanded`.`peis_f_final__Hz` AS `peis_f_final__Hz`,`exp_ec_integration_expanded`.`peis_E_dc__VvsRE` AS `peis_E_dc__VvsRE`,`exp_ec_integration_expanded`.`peis_E_amplitude__VvsRE` AS `peis_E_amplitude__VvsRE`,`exp_ec_integration_expanded`.`peis_R_initialguess__ohm` AS `peis_R_initialguess__ohm`,`exp_ec_integration_expanded`.`peis_points_per_decade` AS `peis_points_per_decade`,`exp_ec_integration_expanded`.`phold_E_hold__VvsRE` AS `phold_E_hold__VvsRE`,`exp_ec_integration_expanded`.`phold_t_hold__s` AS `phold_t_hold__s`,`exp_ec_integration_expanded`.`phold_t_samplerate__s` AS `phold_t_samplerate__s`,`exp_ec_integration_expanded`.`ppulse_E_hold1__VvsRE` AS `ppulse_E_hold1__VvsRE`,`exp_ec_integration_expanded`.`ppulse_E_hold2__VvsRE` AS `ppulse_E_hold2__VvsRE`,`exp_ec_integration_expanded`.`ppulse_t_hold1__s` AS `ppulse_t_hold1__s`,`exp_ec_integration_expanded`.`ppulse_t_hold2__s` AS `ppulse_t_hold2__s`,`exp_ec_integration_expanded`.`ppulse_t_samplerate__s` AS `ppulse_t_samplerate__s`,`exp_ec_integration_expanded`.`ppulse_cycles` AS `ppulse_cycles`,`exp_ec_integration_expanded`.`gpulse_I_hold1__A` AS `gpulse_I_hold1__A`,`exp_ec_integration_expanded`.`gpulse_I_hold2__A` AS `gpulse_I_hold2__A`,`exp_ec_integration_expanded`.`gpulse_t_hold1__s` AS `gpulse_t_hold1__s`,`exp_ec_integration_expanded`.`gpulse_t_hold2__s` AS `gpulse_t_hold2__s`,`exp_ec_integration_expanded`.`gpulse_t_samplerate__s` AS `gpulse_t_samplerate__s`,`exp_ec_integration_expanded`.`gpulse_cycles` AS `gpulse_cycles`,`exp_ec_integration_expanded`.`ramp_E_initial__VvsRE` AS `ramp_E_initial__VvsRE`,`exp_ec_integration_expanded`.`ramp_E_final__VvsRE` AS `ramp_E_final__VvsRE`,`exp_ec_integration_expanded`.`ramp_scanrate__mV_s` AS `ramp_scanrate__mV_s`,`exp_ec_integration_expanded`.`ramp_stepsize__mV` AS `ramp_stepsize__mV`,`exp_ec_integration_expanded`.`ramp_cycles` AS `ramp_cycles`,`exp_ec_integration_expanded`.`fc_top_name_flow_cell` AS `fc_top_name_flow_cell`,`exp_ec_integration_expanded`.`fc_top_name_flow_cell_name_user` AS `fc_top_name_flow_cell_name_user`,`exp_ec_integration_expanded`.`fc_top_name_flow_cell_material` AS `fc_top_name_flow_cell_material`,`exp_ec_integration_expanded`.`fc_top_name_flow_cell_A_opening_ideal__mm2` AS `fc_top_name_flow_cell_A_opening_ideal__mm2`,`exp_ec_integration_expanded`.`fc_top_name_flow_cell_A_opening_real__mm2` AS `fc_top_name_flow_cell_A_opening_real__mm2`,`exp_ec_integration_expanded`.`fc_top_name_flow_cell_manufacture_date` AS `fc_top_name_flow_cell_manufacture_date`,`exp_ec_integration_expanded`.`fc_top_name_flow_cell_CAD_file` AS `fc_top_name_flow_cell_CAD_file`,`exp_ec_integration_expanded`.`fc_top_name_flow_cell_comment` AS `fc_top_name_flow_cell_comment`,`exp_ec_integration_expanded`.`fc_top_id_sealing` AS `fc_top_id_sealing`,`exp_ec_integration_expanded`.`fc_top_id_sealing_name_user` AS `fc_top_id_sealing_name_user`,`exp_ec_integration_expanded`.`fc_top_id_sealing_material` AS `fc_top_id_sealing_material`,`exp_ec_integration_expanded`.`fc_top_id_sealing_A_sealing__mm2` AS `fc_top_id_sealing_A_sealing__mm2`,`exp_ec_integration_expanded`.`fc_top_id_sealing_A_opening__mm2` AS `fc_top_id_sealing_A_opening__mm2`,`exp_ec_integration_expanded`.`fc_top_id_sealing_thickness__mm` AS `fc_top_id_sealing_thickness__mm`,`exp_ec_integration_expanded`.`fc_top_id_sealing_shaping_method` AS `fc_top_id_sealing_shaping_method`,`exp_ec_integration_expanded`.`fc_top_id_sealing_comment` AS `fc_top_id_sealing_comment`,`exp_ec_integration_expanded`.`fc_top_id_PTL` AS `fc_top_id_PTL`,`exp_ec_integration_expanded`.`fc_top_id_PTL_name_user` AS `fc_top_id_PTL_name_user`,`exp_ec_integration_expanded`.`fc_top_id_PTL_material` AS `fc_top_id_PTL_material`,`exp_ec_integration_expanded`.`fc_top_id_PTL_thickness__mm` AS `fc_top_id_PTL_thickness__mm`,`exp_ec_integration_expanded`.`fc_top_id_PTL_manufacturer` AS `fc_top_id_PTL_manufacturer`,`exp_ec_integration_expanded`.`fc_top_id_PTL_A_PTL__mm2` AS `fc_top_id_PTL_A_PTL__mm2`,`exp_ec_integration_expanded`.`fc_top_id_PTL_shaping_method` AS `fc_top_id_PTL_shaping_method`,`exp_ec_integration_expanded`.`fc_top_id_PTL_comment` AS `fc_top_id_PTL_comment`,`exp_ec_integration_expanded`.`fc_bottom_name_flow_cell` AS `fc_bottom_name_flow_cell`,`exp_ec_integration_expanded`.`fc_bottom_name_flow_cell_name_user` AS `fc_bottom_name_flow_cell_name_user`,`exp_ec_integration_expanded`.`fc_bottom_name_flow_cell_material` AS `fc_bottom_name_flow_cell_material`,`exp_ec_integration_expanded`.`fc_bottom_name_flow_cell_A_opening_ideal__mm2` AS `fc_bottom_name_flow_cell_A_opening_ideal__mm2`,`exp_ec_integration_expanded`.`fc_bottom_name_flow_cell_A_opening_real__mm2` AS `fc_bottom_name_flow_cell_A_opening_real__mm2`,`exp_ec_integration_expanded`.`fc_bottom_name_flow_cell_manufacture_date` AS `fc_bottom_name_flow_cell_manufacture_date`,`exp_ec_integration_expanded`.`fc_bottom_name_flow_cell_CAD_file` AS `fc_bottom_name_flow_cell_CAD_file`,`exp_ec_integration_expanded`.`fc_bottom_name_flow_cell_comment` AS `fc_bottom_name_flow_cell_comment`,`exp_ec_integration_expanded`.`fc_bottom_id_sealing` AS `fc_bottom_id_sealing`,`exp_ec_integration_expanded`.`fc_bottom_id_sealing_name_user` AS `fc_bottom_id_sealing_name_user`,`exp_ec_integration_expanded`.`fc_bottom_id_sealing_material` AS `fc_bottom_id_sealing_material`,`exp_ec_integration_expanded`.`fc_bottom_id_sealing_A_sealing__mm2` AS `fc_bottom_id_sealing_A_sealing__mm2`,`exp_ec_integration_expanded`.`fc_bottom_id_sealing_A_opening__mm2` AS `fc_bottom_id_sealing_A_opening__mm2`,`exp_ec_integration_expanded`.`fc_bottom_id_sealing_thickness__mm` AS `fc_bottom_id_sealing_thickness__mm`,`exp_ec_integration_expanded`.`fc_bottom_id_sealing_shaping_method` AS `fc_bottom_id_sealing_shaping_method`,`exp_ec_integration_expanded`.`fc_bottom_id_sealing_comment` AS `fc_bottom_id_sealing_comment`,`exp_ec_integration_expanded`.`fc_bottom_id_PTL` AS `fc_bottom_id_PTL`,`exp_ec_integration_expanded`.`fc_bottom_id_PTL_name_user` AS `fc_bottom_id_PTL_name_user`,`exp_ec_integration_expanded`.`fc_bottom_id_PTL_material` AS `fc_bottom_id_PTL_material`,`exp_ec_integration_expanded`.`fc_bottom_id_PTL_thickness__mm` AS `fc_bottom_id_PTL_thickness__mm`,`exp_ec_integration_expanded`.`fc_bottom_id_PTL_manufacturer` AS `fc_bottom_id_PTL_manufacturer`,`exp_ec_integration_expanded`.`fc_bottom_id_PTL_A_PTL__mm2` AS `fc_bottom_id_PTL_A_PTL__mm2`,`exp_ec_integration_expanded`.`fc_bottom_id_PTL_shaping_method` AS `fc_bottom_id_PTL_shaping_method`,`exp_ec_integration_expanded`.`fc_bottom_id_PTL_comment` AS `fc_bottom_id_PTL_comment`,`exp_ec_integration_expanded`.`fe_top_id_pump_in` AS `fe_top_id_pump_in`,`exp_ec_integration_expanded`.`fe_top_id_pump_in_manufacturer` AS `fe_top_id_pump_in_manufacturer`,`exp_ec_integration_expanded`.`fe_top_id_pump_in_model` AS `fe_top_id_pump_in_model`,`exp_ec_integration_expanded`.`fe_top_id_pump_in_device` AS `fe_top_id_pump_in_device`,`exp_ec_integration_expanded`.`fe_top_id_tubing_in` AS `fe_top_id_tubing_in`,`exp_ec_integration_expanded`.`fe_top_id_tubing_in_name_tubing` AS `fe_top_id_tubing_in_name_tubing`,`exp_ec_integration_expanded`.`fe_top_id_tubing_in_inner_diameter__mm` AS `fe_top_id_tubing_in_inner_diameter__mm`,`exp_ec_integration_expanded`.`fe_top_id_tubing_in_color_code` AS `fe_top_id_tubing_in_color_code`,`exp_ec_integration_expanded`.`fe_top_id_tubing_in_manufacturer` AS `fe_top_id_tubing_in_manufacturer`,`exp_ec_integration_expanded`.`fe_top_id_tubing_in_model` AS `fe_top_id_tubing_in_model`,`exp_ec_integration_expanded`.`fe_top_pump_rate_in__rpm` AS `fe_top_pump_rate_in__rpm`,`exp_ec_integration_expanded`.`fe_top_id_pump_out` AS `fe_top_id_pump_out`,`exp_ec_integration_expanded`.`fe_top_id_pump_out_manufacturer` AS `fe_top_id_pump_out_manufacturer`,`exp_ec_integration_expanded`.`fe_top_id_pump_out_model` AS `fe_top_id_pump_out_model`,`exp_ec_integration_expanded`.`fe_top_id_pump_out_device` AS `fe_top_id_pump_out_device`,`exp_ec_integration_expanded`.`fe_top_id_tubing_out` AS `fe_top_id_tubing_out`,`exp_ec_integration_expanded`.`fe_top_id_tubing_out_name_tubing` AS `fe_top_id_tubing_out_name_tubing`,`exp_ec_integration_expanded`.`fe_top_id_tubing_out_inner_diameter__mm` AS `fe_top_id_tubing_out_inner_diameter__mm`,`exp_ec_integration_expanded`.`fe_top_id_tubing_out_color_code` AS `fe_top_id_tubing_out_color_code`,`exp_ec_integration_expanded`.`fe_top_id_tubing_out_manufacturer` AS `fe_top_id_tubing_out_manufacturer`,`exp_ec_integration_expanded`.`fe_top_id_tubing_out_model` AS `fe_top_id_tubing_out_model`,`exp_ec_integration_expanded`.`fe_top_pump_rate_out__rpm` AS `fe_top_pump_rate_out__rpm`,`exp_ec_integration_expanded`.`fe_top_flow_rate_real__mul_min` AS `fe_top_flow_rate_real__mul_min`,`exp_ec_integration_expanded`.`fe_top_name_electrolyte` AS `fe_top_name_electrolyte`,`exp_ec_integration_expanded`.`fe_top_c_electrolyte__mol_L` AS `fe_top_c_electrolyte__mol_L`,`exp_ec_integration_expanded`.`fe_top_T_electrolyte__degC` AS `fe_top_T_electrolyte__degC`,`exp_ec_integration_expanded`.`fe_bottom_id_pump_in` AS `fe_bottom_id_pump_in`,`exp_ec_integration_expanded`.`fe_bottom_id_pump_in_manufacturer` AS `fe_bottom_id_pump_in_manufacturer`,`exp_ec_integration_expanded`.`fe_bottom_id_pump_in_model` AS `fe_bottom_id_pump_in_model`,`exp_ec_integration_expanded`.`fe_bottom_id_pump_in_device` AS `fe_bottom_id_pump_in_device`,`exp_ec_integration_expanded`.`fe_bottom_id_tubing_in` AS `fe_bottom_id_tubing_in`,`exp_ec_integration_expanded`.`fe_bottom_id_tubing_in_name_tubing` AS `fe_bottom_id_tubing_in_name_tubing`,`exp_ec_integration_expanded`.`fe_bottom_id_tubing_in_inner_diameter__mm` AS `fe_bottom_id_tubing_in_inner_diameter__mm`,`exp_ec_integration_expanded`.`fe_bottom_id_tubing_in_color_code` AS `fe_bottom_id_tubing_in_color_code`,`exp_ec_integration_expanded`.`fe_bottom_id_tubing_in_manufacturer` AS `fe_bottom_id_tubing_in_manufacturer`,`exp_ec_integration_expanded`.`fe_bottom_id_tubing_in_model` AS `fe_bottom_id_tubing_in_model`,`exp_ec_integration_expanded`.`fe_bottom_pump_rate_in__rpm` AS `fe_bottom_pump_rate_in__rpm`,`exp_ec_integration_expanded`.`fe_bottom_id_pump_out` AS `fe_bottom_id_pump_out`,`exp_ec_integration_expanded`.`fe_bottom_id_pump_out_manufacturer` AS `fe_bottom_id_pump_out_manufacturer`,`exp_ec_integration_expanded`.`fe_bottom_id_pump_out_model` AS `fe_bottom_id_pump_out_model`,`exp_ec_integration_expanded`.`fe_bottom_id_pump_out_device` AS `fe_bottom_id_pump_out_device`,`exp_ec_integration_expanded`.`fe_bottom_id_tubing_out` AS `fe_bottom_id_tubing_out`,`exp_ec_integration_expanded`.`fe_bottom_id_tubing_out_name_tubing` AS `fe_bottom_id_tubing_out_name_tubing`,`exp_ec_integration_expanded`.`fe_bottom_id_tubing_out_inner_diameter__mm` AS `fe_bottom_id_tubing_out_inner_diameter__mm`,`exp_ec_integration_expanded`.`fe_bottom_id_tubing_out_color_code` AS `fe_bottom_id_tubing_out_color_code`,`exp_ec_integration_expanded`.`fe_bottom_id_tubing_out_manufacturer` AS `fe_bottom_id_tubing_out_manufacturer`,`exp_ec_integration_expanded`.`fe_bottom_id_tubing_out_model` AS `fe_bottom_id_tubing_out_model`,`exp_ec_integration_expanded`.`fe_bottom_pump_rate_out__rpm` AS `fe_bottom_pump_rate_out__rpm`,`exp_ec_integration_expanded`.`fe_bottom_flow_rate_real__mul_min` AS `fe_bottom_flow_rate_real__mul_min`,`exp_ec_integration_expanded`.`fe_bottom_name_electrolyte` AS `fe_bottom_name_electrolyte`,`exp_ec_integration_expanded`.`fe_bottom_c_electrolyte__mol_L` AS `fe_bottom_c_electrolyte__mol_L`,`exp_ec_integration_expanded`.`fe_bottom_T_electrolyte__degC` AS `fe_bottom_T_electrolyte__degC`,`exp_ec_integration_expanded`.`fg_top_Arring_name_gas` AS `fg_top_Arring_name_gas`,`exp_ec_integration_expanded`.`fg_top_Arring_flow_rate__mL_min` AS `fg_top_Arring_flow_rate__mL_min`,`exp_ec_integration_expanded`.`fg_top_purgevial_name_gas` AS `fg_top_purgevial_name_gas`,`exp_ec_integration_expanded`.`fg_top_purgevial_flow_rate__mL_min` AS `fg_top_purgevial_flow_rate__mL_min`,`exp_ec_integration_expanded`.`fg_top_main_name_gas` AS `fg_top_main_name_gas`,`exp_ec_integration_expanded`.`fg_top_main_flow_rate__mL_min` AS `fg_top_main_flow_rate__mL_min`,`exp_ec_integration_expanded`.`fg_bottom_Arring_name_gas` AS `fg_bottom_Arring_name_gas`,`exp_ec_integration_expanded`.`fg_bottom_Arring_flow_rate__mL_min` AS `fg_bottom_Arring_flow_rate__mL_min`,`exp_ec_integration_expanded`.`fg_bottom_purgevial_name_gas` AS `fg_bottom_purgevial_name_gas`,`exp_ec_integration_expanded`.`fg_bottom_purgevial_flow_rate__mL_min` AS `fg_bottom_purgevial_flow_rate__mL_min`,`exp_ec_integration_expanded`.`fg_bottom_main_name_gas` AS `fg_bottom_main_name_gas`,`exp_ec_integration_expanded`.`fg_bottom_main_flow_rate__mL_min` AS `fg_bottom_main_flow_rate__mL_min`,`exp_ec_integration_expanded`.`n_product_of_interest_simps__mol` AS `n_product_of_interest_simps__mol`,`exp_ec_integration_expanded`.`n_product_of_interest_trapz__mol` AS `n_product_of_interest_trapz__mol`,(`exp_ec_integration_expanded`.`n_product_of_interest_simps__mol` / `exp_icpms_sfc_batch_expanded`.`n_batch__mol`) AS `S_number_simps`,(`exp_ec_integration_expanded`.`n_product_of_interest_trapz__mol` / `exp_icpms_sfc_batch_expanded`.`n_batch__mol`) AS `S_number_trapz` from (`exp_icpms_sfc_batch_expanded` left join `exp_ec_integration_expanded` on(((`exp_icpms_sfc_batch_expanded`.`name_analysis` = `exp_ec_integration_expanded`.`name_analysis`) and (`exp_icpms_sfc_batch_expanded`.`id_exp_ec_dataset` = `exp_ec_integration_expanded`.`id_exp_ec_dataset`) and (`exp_icpms_sfc_batch_expanded`.`name_user` = `exp_ec_integration_expanded`.`name_user`) and (`exp_icpms_sfc_batch_expanded`.`name_setup_sfc` = `exp_ec_integration_expanded`.`name_setup_sfc`)))) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `documentation_columns`
--

/*!50001 DROP VIEW IF EXISTS `documentation_columns`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `documentation_columns` AS select `hte_data_documentation`.`column_information`.`name_table` AS `name_table`,`hte_data_documentation`.`column_information`.`name_column` AS `name_column`,`hte_data_documentation`.`column_information`.`name_inserter` AS `name_inserter`,`hte_data_documentation`.`column_information`.`comment` AS `comment`,`hte_data_documentation`.`column_information`.`name_axislabel__latex` AS `name_axislabel__latex`,`hte_data_documentation`.`column_information`.`table_type` AS `table_type`,`information_schema`.`cols`.`DATA_TYPE` AS `data_type`,(case when (`information_schema`.`cols`.`NUMERIC_PRECISION` is not null) then `information_schema`.`cols`.`NUMERIC_PRECISION` else `information_schema`.`cols`.`CHARACTER_MAXIMUM_LENGTH` end) AS `max_length`,(case when (`information_schema`.`cols`.`DATETIME_PRECISION` is not null) then `information_schema`.`cols`.`DATETIME_PRECISION` when (`information_schema`.`cols`.`NUMERIC_SCALE` is not null) then `information_schema`.`cols`.`NUMERIC_SCALE` else 0 end) AS `precision` from (`hte_data_documentation`.`column_information` left join `information_schema`.`COLUMNS` `cols` on(((`information_schema`.`cols`.`TABLE_NAME` = `hte_data_documentation`.`column_information`.`name_table`) and (`information_schema`.`cols`.`COLUMN_NAME` = `hte_data_documentation`.`column_information`.`name_column`)))) order by `hte_data_documentation`.`column_information`.`name_table` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `documentation_tables`
--

/*!50001 DROP VIEW IF EXISTS `documentation_tables`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `documentation_tables` AS select `information_schema`.`TABLES`.`TABLE_NAME` AS `name_table`,`information_schema`.`TABLES`.`TABLE_COMMENT` AS `comment_table`,`information_schema`.`TABLES`.`TABLE_ROWS` AS `number_rows`,`information_schema`.`TABLES`.`DATA_LENGTH` AS `amount_data`,`information_schema`.`TABLES`.`TABLE_TYPE` AS `table_type`,`hte_data_documentation`.`view_information`.`name_base_table` AS `name_base_table` from (`information_schema`.`TABLES` left join `hte_data_documentation`.`view_information` on((`information_schema`.`TABLES`.`TABLE_NAME` = `hte_data_documentation`.`view_information`.`name_view`))) where (`information_schema`.`TABLES`.`TABLE_SCHEMA` = 'hte_data') */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `exp_ec_expanded`
--

/*!50001 DROP VIEW IF EXISTS `exp_ec_expanded`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `exp_ec_expanded` AS select `exp_sfc`.`id_exp_sfc` AS `id_exp_sfc`,`exp_sfc`.`name_user` AS `name_user`,`exp_sfc`.`name_setup_sfc` AS `name_setup_sfc`,`exp_sfc_name_setup_sfc`.`alias` AS `name_setup_sfc_alias`,`exp_sfc_name_setup_sfc`.`feature` AS `name_setup_sfc_feature`,`exp_sfc_name_setup_sfc`.`type` AS `name_setup_sfc_type`,`exp_sfc`.`t_start__timestamp` AS `t_start__timestamp`,`exp_sfc`.`t_end__timestamp` AS `t_end__timestamp`,`exp_sfc`.`rawdata_path` AS `rawdata_path`,`exp_sfc`.`rawdata_computer` AS `rawdata_computer`,`exp_sfc`.`id_ML` AS `id_ML`,`exp_sfc`.`id_ML_technique` AS `id_ML_technique`,`exp_sfc`.`id_sample` AS `id_sample`,`exp_sfc`.`id_spot` AS `id_spot`,`exp_sfc`.`force__N` AS `force__N`,`exp_sfc`.`T_stage__degC` AS `T_stage__degC`,`exp_sfc`.`interrupted` AS `interrupted`,`exp_sfc`.`labview_sfc_version` AS `labview_sfc_version`,`exp_sfc`.`db_version` AS `db_version`,`exp_sfc`.`comment` AS `comment`,`exp_ec`.`name_technique` AS `ec_name_technique`,`exp_ec`.`R_u__ohm` AS `ec_R_u__ohm`,`exp_ec`.`iR_corr_in_situ__percent` AS `ec_iR_corr_in_situ__percent`,`exp_ec`.`R_u_determining_exp_ec` AS `ec_R_u_determining_exp_ec`,`exp_ec`.`E_RE__VvsRHE` AS `ec_E_RE__VvsRHE`,`exp_ec`.`name_RE` AS `ec_name_RE`,`exp_ec_name_re`.`material` AS `ec_name_RE_material`,`exp_ec_name_re`.`manufacturer` AS `ec_name_RE_manufacturer`,`exp_ec_name_re`.`model` AS `ec_name_RE_model`,`exp_ec`.`name_CE` AS `ec_name_CE`,`exp_ec_name_ce`.`material` AS `ec_name_CE_material`,`exp_ec_name_ce`.`manufacturer` AS `ec_name_CE_manufacturer`,`exp_ec_name_ce`.`model` AS `ec_name_CE_model`,`exp_ec`.`name_device` AS `ec_name_device`,`exp_ec`.`id_control_mode` AS `ec_id_control_mode`,`exp_ec`.`id_ie_range` AS `ec_id_ie_range`,`exp_ec`.`id_vch_range` AS `ec_id_vch_range`,`exp_ec`.`id_ich_range` AS `ec_id_ich_range`,`exp_ec`.`id_vch_filter` AS `ec_id_vch_filter`,`exp_ec`.`id_ich_filter` AS `ec_id_ich_filter`,`exp_ec`.`id_ca_speed` AS `ec_id_ca_speed`,`exp_ec`.`id_ie_stability` AS `ec_id_ie_stability`,`exp_ec`.`id_sampling_mode` AS `ec_id_sampling_mode`,`exp_ec`.`ie_range_auto` AS `ec_ie_range_auto`,`exp_ec`.`vch_range_auto` AS `ec_vch_range_auto`,`exp_ec`.`ich_range_auto` AS `ec_ich_range_auto`,`samples`.`id_sample` AS `samples_id_sample`,`samples`.`name_sample` AS `samples_name_sample`,`samples`.`name_user` AS `samples_name_user`,`samples`.`t_manufactured__timestamp` AS `samples_t_manufactured__timestamp`,`samples`.`comment` AS `samples_comment`,`samples`.`total_loading__mg_cm2` AS `samples_total_loading__mg_cm2`,`spots`.`id_spot` AS `spots_id_spot`,`spots`.`spot_size__mm2` AS `spots_spot_size__mm2`,`spots`.`pos_x__mm` AS `spots_pos_x__mm`,`spots`.`pos_y__mm` AS `spots_pos_y__mm`,`spots`.`comment` AS `spots_comment`,`spots`.`total_loading__mg_cm2` AS `spots_total_loading__mg_cm2`,`exp_ec_cv`.`E_initial__VvsRE` AS `cv_E_initial__VvsRE`,`exp_ec_cv`.`E_apex1__VvsRE` AS `cv_E_apex1__VvsRE`,`exp_ec_cv`.`E_apex2__VvsRE` AS `cv_E_apex2__VvsRE`,`exp_ec_cv`.`E_final__VvsRE` AS `cv_E_final__VvsRE`,`exp_ec_cv`.`scanrate__mV_s` AS `cv_scanrate__mV_s`,`exp_ec_cv`.`stepsize__mV` AS `cv_stepsize__mV`,`exp_ec_cv`.`cycles` AS `cv_cycles`,`exp_ec_geis`.`f_initial__Hz` AS `geis_f_initial__Hz`,`exp_ec_geis`.`f_final__Hz` AS `geis_f_final__Hz`,`exp_ec_geis`.`I_dc__A` AS `geis_I_dc__A`,`exp_ec_geis`.`I_amplitude__A` AS `geis_I_amplitude__A`,`exp_ec_geis`.`R_initialguess__ohm` AS `geis_R_initialguess__ohm`,`exp_ec_geis`.`points_per_decade` AS `geis_points_per_decade`,`exp_ec_ghold`.`I_hold__A` AS `ghold_I_hold__A`,`exp_ec_ghold`.`t_hold__s` AS `ghold_t_hold__s`,`exp_ec_ghold`.`t_samplerate__s` AS `ghold_t_samplerate__s`,`exp_ec_peis`.`f_initial__Hz` AS `peis_f_initial__Hz`,`exp_ec_peis`.`f_final__Hz` AS `peis_f_final__Hz`,`exp_ec_peis`.`E_dc__VvsRE` AS `peis_E_dc__VvsRE`,`exp_ec_peis`.`E_amplitude__VvsRE` AS `peis_E_amplitude__VvsRE`,`exp_ec_peis`.`R_initialguess__ohm` AS `peis_R_initialguess__ohm`,`exp_ec_peis`.`points_per_decade` AS `peis_points_per_decade`,`exp_ec_phold`.`E_hold__VvsRE` AS `phold_E_hold__VvsRE`,`exp_ec_phold`.`t_hold__s` AS `phold_t_hold__s`,`exp_ec_phold`.`t_samplerate__s` AS `phold_t_samplerate__s`,`exp_ec_ppulse`.`E_hold1__VvsRE` AS `ppulse_E_hold1__VvsRE`,`exp_ec_ppulse`.`E_hold2__VvsRE` AS `ppulse_E_hold2__VvsRE`,`exp_ec_ppulse`.`t_hold1__s` AS `ppulse_t_hold1__s`,`exp_ec_ppulse`.`t_hold2__s` AS `ppulse_t_hold2__s`,`exp_ec_ppulse`.`t_samplerate__s` AS `ppulse_t_samplerate__s`,`exp_ec_ppulse`.`cycles` AS `ppulse_cycles`,`exp_ec_gpulse`.`I_hold1__A` AS `gpulse_I_hold1__A`,`exp_ec_gpulse`.`I_hold2__A` AS `gpulse_I_hold2__A`,`exp_ec_gpulse`.`t_hold1__s` AS `gpulse_t_hold1__s`,`exp_ec_gpulse`.`t_hold2__s` AS `gpulse_t_hold2__s`,`exp_ec_gpulse`.`t_samplerate__s` AS `gpulse_t_samplerate__s`,`exp_ec_gpulse`.`cycles` AS `gpulse_cycles`,`exp_ec_ramp`.`E_initial__VvsRE` AS `ramp_E_initial__VvsRE`,`exp_ec_ramp`.`E_final__VvsRE` AS `ramp_E_final__VvsRE`,`exp_ec_ramp`.`scanrate__mV_s` AS `ramp_scanrate__mV_s`,`exp_ec_ramp`.`stepsize__mV` AS `ramp_stepsize__mV`,`exp_ec_ramp`.`cycles` AS `ramp_cycles`,`fc_top`.`name_flow_cell` AS `fc_top_name_flow_cell`,`fc_top_name_flow_cell`.`name_user` AS `fc_top_name_flow_cell_name_user`,`fc_top_name_flow_cell`.`material` AS `fc_top_name_flow_cell_material`,`fc_top_name_flow_cell`.`A_opening_ideal__mm2` AS `fc_top_name_flow_cell_A_opening_ideal__mm2`,`fc_top_name_flow_cell`.`A_opening_real__mm2` AS `fc_top_name_flow_cell_A_opening_real__mm2`,`fc_top_name_flow_cell`.`manufacture_date` AS `fc_top_name_flow_cell_manufacture_date`,`fc_top_name_flow_cell`.`CAD_file` AS `fc_top_name_flow_cell_CAD_file`,`fc_top_name_flow_cell`.`comment` AS `fc_top_name_flow_cell_comment`,`fc_top`.`id_sealing` AS `fc_top_id_sealing`,`fc_top_id_sealing`.`name_user` AS `fc_top_id_sealing_name_user`,`fc_top_id_sealing`.`material` AS `fc_top_id_sealing_material`,`fc_top_id_sealing`.`A_sealing__mm2` AS `fc_top_id_sealing_A_sealing__mm2`,`fc_top_id_sealing`.`A_opening__mm2` AS `fc_top_id_sealing_A_opening__mm2`,`fc_top_id_sealing`.`thickness__mm` AS `fc_top_id_sealing_thickness__mm`,`fc_top_id_sealing`.`shaping_method` AS `fc_top_id_sealing_shaping_method`,`fc_top_id_sealing`.`comment` AS `fc_top_id_sealing_comment`,`fc_top`.`id_PTL` AS `fc_top_id_PTL`,`fc_top_id_ptl`.`name_user` AS `fc_top_id_PTL_name_user`,`fc_top_id_ptl`.`material` AS `fc_top_id_PTL_material`,`fc_top_id_ptl`.`thickness__mm` AS `fc_top_id_PTL_thickness__mm`,`fc_top_id_ptl`.`manufacturer` AS `fc_top_id_PTL_manufacturer`,`fc_top_id_ptl`.`A_PTL__mm2` AS `fc_top_id_PTL_A_PTL__mm2`,`fc_top_id_ptl`.`shaping_method` AS `fc_top_id_PTL_shaping_method`,`fc_top_id_ptl`.`comment` AS `fc_top_id_PTL_comment`,`fc_bottom`.`name_flow_cell` AS `fc_bottom_name_flow_cell`,`fc_bottom_name_flow_cell`.`name_user` AS `fc_bottom_name_flow_cell_name_user`,`fc_bottom_name_flow_cell`.`material` AS `fc_bottom_name_flow_cell_material`,`fc_bottom_name_flow_cell`.`A_opening_ideal__mm2` AS `fc_bottom_name_flow_cell_A_opening_ideal__mm2`,`fc_bottom_name_flow_cell`.`A_opening_real__mm2` AS `fc_bottom_name_flow_cell_A_opening_real__mm2`,`fc_bottom_name_flow_cell`.`manufacture_date` AS `fc_bottom_name_flow_cell_manufacture_date`,`fc_bottom_name_flow_cell`.`CAD_file` AS `fc_bottom_name_flow_cell_CAD_file`,`fc_bottom_name_flow_cell`.`comment` AS `fc_bottom_name_flow_cell_comment`,`fc_bottom`.`id_sealing` AS `fc_bottom_id_sealing`,`fc_bottom_id_sealing`.`name_user` AS `fc_bottom_id_sealing_name_user`,`fc_bottom_id_sealing`.`material` AS `fc_bottom_id_sealing_material`,`fc_bottom_id_sealing`.`A_sealing__mm2` AS `fc_bottom_id_sealing_A_sealing__mm2`,`fc_bottom_id_sealing`.`A_opening__mm2` AS `fc_bottom_id_sealing_A_opening__mm2`,`fc_bottom_id_sealing`.`thickness__mm` AS `fc_bottom_id_sealing_thickness__mm`,`fc_bottom_id_sealing`.`shaping_method` AS `fc_bottom_id_sealing_shaping_method`,`fc_bottom_id_sealing`.`comment` AS `fc_bottom_id_sealing_comment`,`fc_bottom`.`id_PTL` AS `fc_bottom_id_PTL`,`fc_bottom_id_ptl`.`name_user` AS `fc_bottom_id_PTL_name_user`,`fc_bottom_id_ptl`.`material` AS `fc_bottom_id_PTL_material`,`fc_bottom_id_ptl`.`thickness__mm` AS `fc_bottom_id_PTL_thickness__mm`,`fc_bottom_id_ptl`.`manufacturer` AS `fc_bottom_id_PTL_manufacturer`,`fc_bottom_id_ptl`.`A_PTL__mm2` AS `fc_bottom_id_PTL_A_PTL__mm2`,`fc_bottom_id_ptl`.`shaping_method` AS `fc_bottom_id_PTL_shaping_method`,`fc_bottom_id_ptl`.`comment` AS `fc_bottom_id_PTL_comment`,`fe_top`.`id_pump_in` AS `fe_top_id_pump_in`,`fe_top_id_pump_in`.`manufacturer` AS `fe_top_id_pump_in_manufacturer`,`fe_top_id_pump_in`.`model` AS `fe_top_id_pump_in_model`,`fe_top_id_pump_in`.`device` AS `fe_top_id_pump_in_device`,`fe_top`.`id_tubing_in` AS `fe_top_id_tubing_in`,`fe_top_id_tubing_in`.`name_tubing` AS `fe_top_id_tubing_in_name_tubing`,`fe_top_id_tubing_in`.`inner_diameter__mm` AS `fe_top_id_tubing_in_inner_diameter__mm`,`fe_top_id_tubing_in`.`color_code` AS `fe_top_id_tubing_in_color_code`,`fe_top_id_tubing_in`.`manufacturer` AS `fe_top_id_tubing_in_manufacturer`,`fe_top_id_tubing_in`.`model` AS `fe_top_id_tubing_in_model`,`fe_top`.`pump_rate_in__rpm` AS `fe_top_pump_rate_in__rpm`,`fe_top`.`id_pump_out` AS `fe_top_id_pump_out`,`fe_top_id_pump_out`.`manufacturer` AS `fe_top_id_pump_out_manufacturer`,`fe_top_id_pump_out`.`model` AS `fe_top_id_pump_out_model`,`fe_top_id_pump_out`.`device` AS `fe_top_id_pump_out_device`,`fe_top`.`id_tubing_out` AS `fe_top_id_tubing_out`,`fe_top_id_tubing_out`.`name_tubing` AS `fe_top_id_tubing_out_name_tubing`,`fe_top_id_tubing_out`.`inner_diameter__mm` AS `fe_top_id_tubing_out_inner_diameter__mm`,`fe_top_id_tubing_out`.`color_code` AS `fe_top_id_tubing_out_color_code`,`fe_top_id_tubing_out`.`manufacturer` AS `fe_top_id_tubing_out_manufacturer`,`fe_top_id_tubing_out`.`model` AS `fe_top_id_tubing_out_model`,`fe_top`.`pump_rate_out__rpm` AS `fe_top_pump_rate_out__rpm`,`fe_top`.`flow_rate_real__mul_min` AS `fe_top_flow_rate_real__mul_min`,`fe_top`.`name_electrolyte` AS `fe_top_name_electrolyte`,`fe_top`.`c_electrolyte__mol_L` AS `fe_top_c_electrolyte__mol_L`,`fe_top`.`T_electrolyte__degC` AS `fe_top_T_electrolyte__degC`,`fe_bottom`.`id_pump_in` AS `fe_bottom_id_pump_in`,`fe_bottom_id_pump_in`.`manufacturer` AS `fe_bottom_id_pump_in_manufacturer`,`fe_bottom_id_pump_in`.`model` AS `fe_bottom_id_pump_in_model`,`fe_bottom_id_pump_in`.`device` AS `fe_bottom_id_pump_in_device`,`fe_bottom`.`id_tubing_in` AS `fe_bottom_id_tubing_in`,`fe_bottom_id_tubing_in`.`name_tubing` AS `fe_bottom_id_tubing_in_name_tubing`,`fe_bottom_id_tubing_in`.`inner_diameter__mm` AS `fe_bottom_id_tubing_in_inner_diameter__mm`,`fe_bottom_id_tubing_in`.`color_code` AS `fe_bottom_id_tubing_in_color_code`,`fe_bottom_id_tubing_in`.`manufacturer` AS `fe_bottom_id_tubing_in_manufacturer`,`fe_bottom_id_tubing_in`.`model` AS `fe_bottom_id_tubing_in_model`,`fe_bottom`.`pump_rate_in__rpm` AS `fe_bottom_pump_rate_in__rpm`,`fe_bottom`.`id_pump_out` AS `fe_bottom_id_pump_out`,`fe_bottom_id_pump_out`.`manufacturer` AS `fe_bottom_id_pump_out_manufacturer`,`fe_bottom_id_pump_out`.`model` AS `fe_bottom_id_pump_out_model`,`fe_bottom_id_pump_out`.`device` AS `fe_bottom_id_pump_out_device`,`fe_bottom`.`id_tubing_out` AS `fe_bottom_id_tubing_out`,`fe_bottom_id_tubing_out`.`name_tubing` AS `fe_bottom_id_tubing_out_name_tubing`,`fe_bottom_id_tubing_out`.`inner_diameter__mm` AS `fe_bottom_id_tubing_out_inner_diameter__mm`,`fe_bottom_id_tubing_out`.`color_code` AS `fe_bottom_id_tubing_out_color_code`,`fe_bottom_id_tubing_out`.`manufacturer` AS `fe_bottom_id_tubing_out_manufacturer`,`fe_bottom_id_tubing_out`.`model` AS `fe_bottom_id_tubing_out_model`,`fe_bottom`.`pump_rate_out__rpm` AS `fe_bottom_pump_rate_out__rpm`,`fe_bottom`.`flow_rate_real__mul_min` AS `fe_bottom_flow_rate_real__mul_min`,`fe_bottom`.`name_electrolyte` AS `fe_bottom_name_electrolyte`,`fe_bottom`.`c_electrolyte__mol_L` AS `fe_bottom_c_electrolyte__mol_L`,`fe_bottom`.`T_electrolyte__degC` AS `fe_bottom_T_electrolyte__degC`,`fg_top_arring`.`name_gas` AS `fg_top_Arring_name_gas`,`fg_top_arring`.`flow_rate__mL_min` AS `fg_top_Arring_flow_rate__mL_min`,`fg_top_purgevial`.`name_gas` AS `fg_top_purgevial_name_gas`,`fg_top_purgevial`.`flow_rate__mL_min` AS `fg_top_purgevial_flow_rate__mL_min`,`fg_top_main`.`name_gas` AS `fg_top_main_name_gas`,`fg_top_main`.`flow_rate__mL_min` AS `fg_top_main_flow_rate__mL_min`,`fg_bottom_arring`.`name_gas` AS `fg_bottom_Arring_name_gas`,`fg_bottom_arring`.`flow_rate__mL_min` AS `fg_bottom_Arring_flow_rate__mL_min`,`fg_bottom_purgevial`.`name_gas` AS `fg_bottom_purgevial_name_gas`,`fg_bottom_purgevial`.`flow_rate__mL_min` AS `fg_bottom_purgevial_flow_rate__mL_min`,`fg_bottom_main`.`name_gas` AS `fg_bottom_main_name_gas`,`fg_bottom_main`.`flow_rate__mL_min` AS `fg_bottom_main_flow_rate__mL_min` from ((((((((((((((((((((((((((((((((((((((`exp_sfc` left join `exp_ec` on((`exp_sfc`.`id_exp_sfc` = `exp_ec`.`id_exp_sfc`))) left join `samples` on((`exp_sfc`.`id_sample` = `samples`.`id_sample`))) left join `spots` on(((`exp_sfc`.`id_sample` = `spots`.`id_sample`) and (`exp_sfc`.`id_spot` = `spots`.`id_spot`)))) left join `exp_ec_cv` on((`exp_sfc`.`id_exp_sfc` = `exp_ec_cv`.`id_exp_sfc`))) left join `exp_ec_geis` on((`exp_sfc`.`id_exp_sfc` = `exp_ec_geis`.`id_exp_sfc`))) left join `exp_ec_ghold` on((`exp_sfc`.`id_exp_sfc` = `exp_ec_ghold`.`id_exp_sfc`))) left join `exp_ec_peis` on((`exp_sfc`.`id_exp_sfc` = `exp_ec_peis`.`id_exp_sfc`))) left join `exp_ec_phold` on((`exp_sfc`.`id_exp_sfc` = `exp_ec_phold`.`id_exp_sfc`))) left join `exp_ec_ppulse` on((`exp_sfc`.`id_exp_sfc` = `exp_ec_ppulse`.`id_exp_sfc`))) left join `exp_ec_gpulse` on((`exp_sfc`.`id_exp_sfc` = `exp_ec_gpulse`.`id_exp_sfc`))) left join `exp_ec_ramp` on((`exp_sfc`.`id_exp_sfc` = `exp_ec_ramp`.`id_exp_sfc`))) left join `flow_cell_assemblies` `fc_top` on(((`exp_ec`.`id_exp_sfc` = `fc_top`.`id_exp_sfc`) and (`fc_top`.`location` = 'top')))) left join `flow_cell_assemblies` `fc_bottom` on(((`exp_ec`.`id_exp_sfc` = `fc_bottom`.`id_exp_sfc`) and (`fc_bottom`.`location` = 'bottom')))) left join `flow_electrolyte` `fe_top` on(((`exp_ec`.`id_exp_sfc` = `fe_top`.`id_exp_sfc`) and (`fe_top`.`location` = 'top')))) left join `flow_electrolyte` `fe_bottom` on(((`exp_ec`.`id_exp_sfc` = `fe_bottom`.`id_exp_sfc`) and (`fe_bottom`.`location` = 'bottom')))) left join `flow_gas` `fg_top_arring` on(((`exp_ec`.`id_exp_sfc` = `fg_top_arring`.`id_exp_sfc`) and (`fg_top_arring`.`location` = 'top') and (`fg_top_arring`.`function` = 'Arring')))) left join `flow_gas` `fg_top_purgevial` on(((`exp_ec`.`id_exp_sfc` = `fg_top_purgevial`.`id_exp_sfc`) and (`fg_top_purgevial`.`location` = 'top') and (`fg_top_purgevial`.`function` = 'purgevial')))) left join `flow_gas` `fg_top_main` on(((`exp_ec`.`id_exp_sfc` = `fg_top_main`.`id_exp_sfc`) and (`fg_top_main`.`location` = 'top') and (`fg_top_main`.`function` = 'main')))) left join `flow_gas` `fg_bottom_arring` on(((`exp_ec`.`id_exp_sfc` = `fg_bottom_arring`.`id_exp_sfc`) and (`fg_bottom_arring`.`location` = 'bottom') and (`fg_bottom_arring`.`function` = 'Arring')))) left join `flow_gas` `fg_bottom_purgevial` on(((`exp_ec`.`id_exp_sfc` = `fg_bottom_purgevial`.`id_exp_sfc`) and (`fg_bottom_purgevial`.`location` = 'bottom') and (`fg_bottom_purgevial`.`function` = 'purgevial')))) left join `flow_gas` `fg_bottom_main` on(((`exp_ec`.`id_exp_sfc` = `fg_bottom_main`.`id_exp_sfc`) and (`fg_bottom_main`.`location` = 'bottom') and (`fg_bottom_main`.`function` = 'main')))) left join `setups_sfc` `exp_sfc_name_setup_sfc` on((`exp_sfc`.`name_setup_sfc` = `exp_sfc_name_setup_sfc`.`name_setup_sfc`))) left join `reference_electrodes` `exp_ec_name_re` on((`exp_ec`.`name_RE` = `exp_ec_name_re`.`name_RE`))) left join `counter_electrodes` `exp_ec_name_ce` on((`exp_ec`.`name_CE` = `exp_ec_name_ce`.`name_CE`))) left join `flow_cells` `fc_top_name_flow_cell` on((`fc_top`.`name_flow_cell` = `fc_top_name_flow_cell`.`name_flow_cell`))) left join `sealings` `fc_top_id_sealing` on((`fc_top`.`id_sealing` = `fc_top_id_sealing`.`id_sealing`))) left join `porous_transport_layers` `fc_top_id_ptl` on((`fc_top`.`id_PTL` = `fc_top_id_ptl`.`id_PTL`))) left join `flow_cells` `fc_bottom_name_flow_cell` on((`fc_bottom`.`name_flow_cell` = `fc_bottom_name_flow_cell`.`name_flow_cell`))) left join `sealings` `fc_bottom_id_sealing` on((`fc_bottom`.`id_sealing` = `fc_bottom_id_sealing`.`id_sealing`))) left join `porous_transport_layers` `fc_bottom_id_ptl` on((`fc_bottom`.`id_PTL` = `fc_bottom_id_ptl`.`id_PTL`))) left join `peristaltic_pumps` `fe_top_id_pump_in` on((`fe_top`.`id_pump_in` = `fe_top_id_pump_in`.`id_pump`))) left join `peristaltic_tubings` `fe_top_id_tubing_in` on((`fe_top`.`id_tubing_in` = `fe_top_id_tubing_in`.`id_tubing`))) left join `peristaltic_pumps` `fe_top_id_pump_out` on((`fe_top`.`id_pump_out` = `fe_top_id_pump_out`.`id_pump`))) left join `peristaltic_tubings` `fe_top_id_tubing_out` on((`fe_top`.`id_tubing_out` = `fe_top_id_tubing_out`.`id_tubing`))) left join `peristaltic_pumps` `fe_bottom_id_pump_in` on((`fe_bottom`.`id_pump_in` = `fe_bottom_id_pump_in`.`id_pump`))) left join `peristaltic_tubings` `fe_bottom_id_tubing_in` on((`fe_bottom`.`id_tubing_in` = `fe_bottom_id_tubing_in`.`id_tubing`))) left join `peristaltic_pumps` `fe_bottom_id_pump_out` on((`fe_bottom`.`id_pump_out` = `fe_bottom_id_pump_out`.`id_pump`))) left join `peristaltic_tubings` `fe_bottom_id_tubing_out` on((`fe_bottom`.`id_tubing_out` = `fe_bottom_id_tubing_out`.`id_tubing`))) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `exp_ec_expanded_old`
--

/*!50001 DROP VIEW IF EXISTS `exp_ec_expanded_old`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `exp_ec_expanded_old` AS select `exp_sfc`.`id_exp_sfc` AS `id_exp_sfc`,`exp_sfc`.`name_user` AS `name_user`,`exp_sfc`.`name_setup_sfc` AS `name_setup_sfc`,`exp_sfc_name_setup_sfc`.`alias` AS `name_setup_sfc_alias`,`exp_sfc_name_setup_sfc`.`feature` AS `name_setup_sfc_feature`,`exp_sfc_name_setup_sfc`.`type` AS `name_setup_sfc_type`,`exp_sfc`.`t_start__timestamp` AS `t_start__timestamp`,`exp_sfc`.`rawdata_path` AS `rawdata_path`,`exp_sfc`.`rawdata_computer` AS `rawdata_computer`,`exp_sfc`.`id_ML` AS `id_ML`,`exp_sfc`.`id_ML_technique` AS `id_ML_technique`,`exp_sfc`.`id_sample` AS `id_sample`,`exp_sfc`.`id_spot` AS `id_spot`,`exp_sfc`.`force__N` AS `force__N`,`exp_sfc`.`T_stage__degC` AS `T_stage__degC`,`exp_sfc`.`interrupted` AS `interrupted`,`exp_sfc`.`labview_sfc_version` AS `labview_sfc_version`,`exp_sfc`.`db_version` AS `db_version`,`exp_sfc`.`comment` AS `comment`,`t_duration_calc`.`t_duration__s` AS `t_duration__s`,(`exp_sfc`.`t_start__timestamp` + interval `t_duration_calc`.`t_duration__s` second) AS `t_end__timestamp`,`exp_ec`.`name_technique` AS `ec_name_technique`,`exp_ec`.`R_u__ohm` AS `ec_R_u__ohm`,`exp_ec`.`iR_corr_in_situ__percent` AS `ec_iR_corr_in_situ__percent`,`exp_ec`.`R_u_determining_exp_ec` AS `ec_R_u_determining_exp_ec`,`exp_ec`.`E_RE__VvsRHE` AS `ec_E_RE__VvsRHE`,`exp_ec`.`name_RE` AS `ec_name_RE`,`exp_ec_name_re`.`material` AS `ec_name_RE_material`,`exp_ec_name_re`.`manufacturer` AS `ec_name_RE_manufacturer`,`exp_ec_name_re`.`model` AS `ec_name_RE_model`,`exp_ec`.`name_CE` AS `ec_name_CE`,`exp_ec_name_ce`.`material` AS `ec_name_CE_material`,`exp_ec_name_ce`.`manufacturer` AS `ec_name_CE_manufacturer`,`exp_ec_name_ce`.`model` AS `ec_name_CE_model`,`exp_ec`.`name_device` AS `ec_name_device`,`exp_ec`.`id_control_mode` AS `ec_id_control_mode`,`exp_ec`.`id_ie_range` AS `ec_id_ie_range`,`exp_ec`.`id_vch_range` AS `ec_id_vch_range`,`exp_ec`.`id_ich_range` AS `ec_id_ich_range`,`exp_ec`.`id_vch_filter` AS `ec_id_vch_filter`,`exp_ec`.`id_ich_filter` AS `ec_id_ich_filter`,`exp_ec`.`id_ca_speed` AS `ec_id_ca_speed`,`exp_ec`.`id_ie_stability` AS `ec_id_ie_stability`,`exp_ec`.`id_sampling_mode` AS `ec_id_sampling_mode`,`exp_ec`.`ie_range_auto` AS `ec_ie_range_auto`,`exp_ec`.`vch_range_auto` AS `ec_vch_range_auto`,`exp_ec`.`ich_range_auto` AS `ec_ich_range_auto`,`samples`.`id_sample` AS `samples_id_sample`,`samples`.`name_sample` AS `samples_name_sample`,`samples`.`name_user` AS `samples_name_user`,`samples`.`t_manufactured__timestamp` AS `samples_t_manufactured__timestamp`,`samples`.`comment` AS `samples_comment`,`samples`.`total_loading__mg_cm2` AS `samples_total_loading__mg_cm2`,`spots`.`id_spot` AS `spots_id_spot`,`spots`.`spot_size__mm2` AS `spots_spot_size__mm2`,`spots`.`pos_x__mm` AS `spots_pos_x__mm`,`spots`.`pos_y__mm` AS `spots_pos_y__mm`,`spots`.`comment` AS `spots_comment`,`spots`.`total_loading__mg_cm2` AS `spots_total_loading__mg_cm2`,`exp_ec_cv`.`E_initial__VvsRE` AS `cv_E_initial__VvsRE`,`exp_ec_cv`.`E_apex1__VvsRE` AS `cv_E_apex1__VvsRE`,`exp_ec_cv`.`E_apex2__VvsRE` AS `cv_E_apex2__VvsRE`,`exp_ec_cv`.`E_final__VvsRE` AS `cv_E_final__VvsRE`,`exp_ec_cv`.`scanrate__mV_s` AS `cv_scanrate__mV_s`,`exp_ec_cv`.`stepsize__mV` AS `cv_stepsize__mV`,`exp_ec_cv`.`cycles` AS `cv_cycles`,`exp_ec_geis`.`f_initial__Hz` AS `geis_f_initial__Hz`,`exp_ec_geis`.`f_final__Hz` AS `geis_f_final__Hz`,`exp_ec_geis`.`I_dc__A` AS `geis_I_dc__A`,`exp_ec_geis`.`I_amplitude__A` AS `geis_I_amplitude__A`,`exp_ec_geis`.`R_initialguess__ohm` AS `geis_R_initialguess__ohm`,`exp_ec_geis`.`points_per_decade` AS `geis_points_per_decade`,`exp_ec_ghold`.`I_hold__A` AS `ghold_I_hold__A`,`exp_ec_ghold`.`t_hold__s` AS `ghold_t_hold__s`,`exp_ec_ghold`.`t_samplerate__s` AS `ghold_t_samplerate__s`,`exp_ec_peis`.`f_initial__Hz` AS `peis_f_initial__Hz`,`exp_ec_peis`.`f_final__Hz` AS `peis_f_final__Hz`,`exp_ec_peis`.`E_dc__VvsRE` AS `peis_E_dc__VvsRE`,`exp_ec_peis`.`E_amplitude__VvsRE` AS `peis_E_amplitude__VvsRE`,`exp_ec_peis`.`R_initialguess__ohm` AS `peis_R_initialguess__ohm`,`exp_ec_peis`.`points_per_decade` AS `peis_points_per_decade`,`exp_ec_phold`.`E_hold__VvsRE` AS `phold_E_hold__VvsRE`,`exp_ec_phold`.`t_hold__s` AS `phold_t_hold__s`,`exp_ec_phold`.`t_samplerate__s` AS `phold_t_samplerate__s`,`exp_ec_ppulse`.`E_hold1__VvsRE` AS `ppulse_E_hold1__VvsRE`,`exp_ec_ppulse`.`E_hold2__VvsRE` AS `ppulse_E_hold2__VvsRE`,`exp_ec_ppulse`.`t_hold1__s` AS `ppulse_t_hold1__s`,`exp_ec_ppulse`.`t_hold2__s` AS `ppulse_t_hold2__s`,`exp_ec_ppulse`.`t_samplerate__s` AS `ppulse_t_samplerate__s`,`exp_ec_ppulse`.`cycles` AS `ppulse_cycles`,`exp_ec_gpulse`.`I_hold1__A` AS `gpulse_I_hold1__A`,`exp_ec_gpulse`.`I_hold2__A` AS `gpulse_I_hold2__A`,`exp_ec_gpulse`.`t_hold1__s` AS `gpulse_t_hold1__s`,`exp_ec_gpulse`.`t_hold2__s` AS `gpulse_t_hold2__s`,`exp_ec_gpulse`.`t_samplerate__s` AS `gpulse_t_samplerate__s`,`exp_ec_gpulse`.`cycles` AS `gpulse_cycles`,`exp_ec_ramp`.`E_initial__VvsRE` AS `ramp_E_initial__VvsRE`,`exp_ec_ramp`.`E_final__VvsRE` AS `ramp_E_final__VvsRE`,`exp_ec_ramp`.`scanrate__mV_s` AS `ramp_scanrate__mV_s`,`exp_ec_ramp`.`stepsize__mV` AS `ramp_stepsize__mV`,`exp_ec_ramp`.`cycles` AS `ramp_cycles`,`fc_top`.`name_flow_cell` AS `fc_top_name_flow_cell`,`fc_top_name_flow_cell`.`name_user` AS `fc_top_name_flow_cell_name_user`,`fc_top_name_flow_cell`.`material` AS `fc_top_name_flow_cell_material`,`fc_top_name_flow_cell`.`A_opening_ideal__mm2` AS `fc_top_name_flow_cell_A_opening_ideal__mm2`,`fc_top_name_flow_cell`.`A_opening_real__mm2` AS `fc_top_name_flow_cell_A_opening_real__mm2`,`fc_top_name_flow_cell`.`manufacture_date` AS `fc_top_name_flow_cell_manufacture_date`,`fc_top_name_flow_cell`.`CAD_file` AS `fc_top_name_flow_cell_CAD_file`,`fc_top_name_flow_cell`.`comment` AS `fc_top_name_flow_cell_comment`,`fc_top`.`id_sealing` AS `fc_top_id_sealing`,`fc_top_id_sealing`.`name_user` AS `fc_top_id_sealing_name_user`,`fc_top_id_sealing`.`material` AS `fc_top_id_sealing_material`,`fc_top_id_sealing`.`A_sealing__mm2` AS `fc_top_id_sealing_A_sealing__mm2`,`fc_top_id_sealing`.`A_opening__mm2` AS `fc_top_id_sealing_A_opening__mm2`,`fc_top_id_sealing`.`thickness__mm` AS `fc_top_id_sealing_thickness__mm`,`fc_top_id_sealing`.`shaping_method` AS `fc_top_id_sealing_shaping_method`,`fc_top_id_sealing`.`comment` AS `fc_top_id_sealing_comment`,`fc_top`.`id_PTL` AS `fc_top_id_PTL`,`fc_top_id_ptl`.`name_user` AS `fc_top_id_PTL_name_user`,`fc_top_id_ptl`.`material` AS `fc_top_id_PTL_material`,`fc_top_id_ptl`.`thickness__mm` AS `fc_top_id_PTL_thickness__mm`,`fc_top_id_ptl`.`manufacturer` AS `fc_top_id_PTL_manufacturer`,`fc_top_id_ptl`.`A_PTL__mm2` AS `fc_top_id_PTL_A_PTL__mm2`,`fc_top_id_ptl`.`shaping_method` AS `fc_top_id_PTL_shaping_method`,`fc_top_id_ptl`.`comment` AS `fc_top_id_PTL_comment`,`fc_bottom`.`name_flow_cell` AS `fc_bottom_name_flow_cell`,`fc_bottom_name_flow_cell`.`name_user` AS `fc_bottom_name_flow_cell_name_user`,`fc_bottom_name_flow_cell`.`material` AS `fc_bottom_name_flow_cell_material`,`fc_bottom_name_flow_cell`.`A_opening_ideal__mm2` AS `fc_bottom_name_flow_cell_A_opening_ideal__mm2`,`fc_bottom_name_flow_cell`.`A_opening_real__mm2` AS `fc_bottom_name_flow_cell_A_opening_real__mm2`,`fc_bottom_name_flow_cell`.`manufacture_date` AS `fc_bottom_name_flow_cell_manufacture_date`,`fc_bottom_name_flow_cell`.`CAD_file` AS `fc_bottom_name_flow_cell_CAD_file`,`fc_bottom_name_flow_cell`.`comment` AS `fc_bottom_name_flow_cell_comment`,`fc_bottom`.`id_sealing` AS `fc_bottom_id_sealing`,`fc_bottom_id_sealing`.`name_user` AS `fc_bottom_id_sealing_name_user`,`fc_bottom_id_sealing`.`material` AS `fc_bottom_id_sealing_material`,`fc_bottom_id_sealing`.`A_sealing__mm2` AS `fc_bottom_id_sealing_A_sealing__mm2`,`fc_bottom_id_sealing`.`A_opening__mm2` AS `fc_bottom_id_sealing_A_opening__mm2`,`fc_bottom_id_sealing`.`thickness__mm` AS `fc_bottom_id_sealing_thickness__mm`,`fc_bottom_id_sealing`.`shaping_method` AS `fc_bottom_id_sealing_shaping_method`,`fc_bottom_id_sealing`.`comment` AS `fc_bottom_id_sealing_comment`,`fc_bottom`.`id_PTL` AS `fc_bottom_id_PTL`,`fc_bottom_id_ptl`.`name_user` AS `fc_bottom_id_PTL_name_user`,`fc_bottom_id_ptl`.`material` AS `fc_bottom_id_PTL_material`,`fc_bottom_id_ptl`.`thickness__mm` AS `fc_bottom_id_PTL_thickness__mm`,`fc_bottom_id_ptl`.`manufacturer` AS `fc_bottom_id_PTL_manufacturer`,`fc_bottom_id_ptl`.`A_PTL__mm2` AS `fc_bottom_id_PTL_A_PTL__mm2`,`fc_bottom_id_ptl`.`shaping_method` AS `fc_bottom_id_PTL_shaping_method`,`fc_bottom_id_ptl`.`comment` AS `fc_bottom_id_PTL_comment`,`fe_top`.`id_pump_in` AS `fe_top_id_pump_in`,`fe_top_id_pump_in`.`manufacturer` AS `fe_top_id_pump_in_manufacturer`,`fe_top_id_pump_in`.`model` AS `fe_top_id_pump_in_model`,`fe_top_id_pump_in`.`device` AS `fe_top_id_pump_in_device`,`fe_top`.`id_tubing_in` AS `fe_top_id_tubing_in`,`fe_top_id_tubing_in`.`name_tubing` AS `fe_top_id_tubing_in_name_tubing`,`fe_top_id_tubing_in`.`inner_diameter__mm` AS `fe_top_id_tubing_in_inner_diameter__mm`,`fe_top_id_tubing_in`.`color_code` AS `fe_top_id_tubing_in_color_code`,`fe_top_id_tubing_in`.`manufacturer` AS `fe_top_id_tubing_in_manufacturer`,`fe_top_id_tubing_in`.`model` AS `fe_top_id_tubing_in_model`,`fe_top`.`pump_rate_in__rpm` AS `fe_top_pump_rate_in__rpm`,`fe_top`.`id_pump_out` AS `fe_top_id_pump_out`,`fe_top_id_pump_out`.`manufacturer` AS `fe_top_id_pump_out_manufacturer`,`fe_top_id_pump_out`.`model` AS `fe_top_id_pump_out_model`,`fe_top_id_pump_out`.`device` AS `fe_top_id_pump_out_device`,`fe_top`.`id_tubing_out` AS `fe_top_id_tubing_out`,`fe_top_id_tubing_out`.`name_tubing` AS `fe_top_id_tubing_out_name_tubing`,`fe_top_id_tubing_out`.`inner_diameter__mm` AS `fe_top_id_tubing_out_inner_diameter__mm`,`fe_top_id_tubing_out`.`color_code` AS `fe_top_id_tubing_out_color_code`,`fe_top_id_tubing_out`.`manufacturer` AS `fe_top_id_tubing_out_manufacturer`,`fe_top_id_tubing_out`.`model` AS `fe_top_id_tubing_out_model`,`fe_top`.`pump_rate_out__rpm` AS `fe_top_pump_rate_out__rpm`,`fe_top`.`flow_rate_real__mul_min` AS `fe_top_flow_rate_real__mul_min`,`fe_top`.`name_electrolyte` AS `fe_top_name_electrolyte`,`fe_top`.`c_electrolyte__mol_L` AS `fe_top_c_electrolyte__mol_L`,`fe_top`.`T_electrolyte__degC` AS `fe_top_T_electrolyte__degC`,`fe_bottom`.`id_pump_in` AS `fe_bottom_id_pump_in`,`fe_bottom_id_pump_in`.`manufacturer` AS `fe_bottom_id_pump_in_manufacturer`,`fe_bottom_id_pump_in`.`model` AS `fe_bottom_id_pump_in_model`,`fe_bottom_id_pump_in`.`device` AS `fe_bottom_id_pump_in_device`,`fe_bottom`.`id_tubing_in` AS `fe_bottom_id_tubing_in`,`fe_bottom_id_tubing_in`.`name_tubing` AS `fe_bottom_id_tubing_in_name_tubing`,`fe_bottom_id_tubing_in`.`inner_diameter__mm` AS `fe_bottom_id_tubing_in_inner_diameter__mm`,`fe_bottom_id_tubing_in`.`color_code` AS `fe_bottom_id_tubing_in_color_code`,`fe_bottom_id_tubing_in`.`manufacturer` AS `fe_bottom_id_tubing_in_manufacturer`,`fe_bottom_id_tubing_in`.`model` AS `fe_bottom_id_tubing_in_model`,`fe_bottom`.`pump_rate_in__rpm` AS `fe_bottom_pump_rate_in__rpm`,`fe_bottom`.`id_pump_out` AS `fe_bottom_id_pump_out`,`fe_bottom_id_pump_out`.`manufacturer` AS `fe_bottom_id_pump_out_manufacturer`,`fe_bottom_id_pump_out`.`model` AS `fe_bottom_id_pump_out_model`,`fe_bottom_id_pump_out`.`device` AS `fe_bottom_id_pump_out_device`,`fe_bottom`.`id_tubing_out` AS `fe_bottom_id_tubing_out`,`fe_bottom_id_tubing_out`.`name_tubing` AS `fe_bottom_id_tubing_out_name_tubing`,`fe_bottom_id_tubing_out`.`inner_diameter__mm` AS `fe_bottom_id_tubing_out_inner_diameter__mm`,`fe_bottom_id_tubing_out`.`color_code` AS `fe_bottom_id_tubing_out_color_code`,`fe_bottom_id_tubing_out`.`manufacturer` AS `fe_bottom_id_tubing_out_manufacturer`,`fe_bottom_id_tubing_out`.`model` AS `fe_bottom_id_tubing_out_model`,`fe_bottom`.`pump_rate_out__rpm` AS `fe_bottom_pump_rate_out__rpm`,`fe_bottom`.`flow_rate_real__mul_min` AS `fe_bottom_flow_rate_real__mul_min`,`fe_bottom`.`name_electrolyte` AS `fe_bottom_name_electrolyte`,`fe_bottom`.`c_electrolyte__mol_L` AS `fe_bottom_c_electrolyte__mol_L`,`fe_bottom`.`T_electrolyte__degC` AS `fe_bottom_T_electrolyte__degC`,`fg_top_arring`.`name_gas` AS `fg_top_Arring_name_gas`,`fg_top_arring`.`flow_rate__mL_min` AS `fg_top_Arring_flow_rate__mL_min`,`fg_top_purgevial`.`name_gas` AS `fg_top_purgevial_name_gas`,`fg_top_purgevial`.`flow_rate__mL_min` AS `fg_top_purgevial_flow_rate__mL_min`,`fg_top_main`.`name_gas` AS `fg_top_main_name_gas`,`fg_top_main`.`flow_rate__mL_min` AS `fg_top_main_flow_rate__mL_min`,`fg_bottom_arring`.`name_gas` AS `fg_bottom_Arring_name_gas`,`fg_bottom_arring`.`flow_rate__mL_min` AS `fg_bottom_Arring_flow_rate__mL_min`,`fg_bottom_purgevial`.`name_gas` AS `fg_bottom_purgevial_name_gas`,`fg_bottom_purgevial`.`flow_rate__mL_min` AS `fg_bottom_purgevial_flow_rate__mL_min`,`fg_bottom_main`.`name_gas` AS `fg_bottom_main_name_gas`,`fg_bottom_main`.`flow_rate__mL_min` AS `fg_bottom_main_flow_rate__mL_min` from (((((((((((((((((((((((((((((((((((((((`exp_sfc` left join `exp_ec` on((`exp_sfc`.`id_exp_sfc` = `exp_ec`.`id_exp_sfc`))) left join `samples` on((`exp_sfc`.`id_sample` = `samples`.`id_sample`))) left join `spots` on(((`exp_sfc`.`id_sample` = `spots`.`id_sample`) and (`exp_sfc`.`id_spot` = `spots`.`id_spot`)))) left join (select `data_ec`.`id_exp_sfc` AS `id_exp_sfc`,max(`data_ec`.`t__s`) AS `t_duration__s` from `data_ec` group by `data_ec`.`id_exp_sfc`) `t_duration_calc` on((`exp_sfc`.`id_exp_sfc` = `t_duration_calc`.`id_exp_sfc`))) left join `exp_ec_cv` on((`exp_sfc`.`id_exp_sfc` = `exp_ec_cv`.`id_exp_sfc`))) left join `exp_ec_geis` on((`exp_sfc`.`id_exp_sfc` = `exp_ec_geis`.`id_exp_sfc`))) left join `exp_ec_ghold` on((`exp_sfc`.`id_exp_sfc` = `exp_ec_ghold`.`id_exp_sfc`))) left join `exp_ec_peis` on((`exp_sfc`.`id_exp_sfc` = `exp_ec_peis`.`id_exp_sfc`))) left join `exp_ec_phold` on((`exp_sfc`.`id_exp_sfc` = `exp_ec_phold`.`id_exp_sfc`))) left join `exp_ec_ppulse` on((`exp_sfc`.`id_exp_sfc` = `exp_ec_ppulse`.`id_exp_sfc`))) left join `exp_ec_gpulse` on((`exp_sfc`.`id_exp_sfc` = `exp_ec_gpulse`.`id_exp_sfc`))) left join `exp_ec_ramp` on((`exp_sfc`.`id_exp_sfc` = `exp_ec_ramp`.`id_exp_sfc`))) left join `flow_cell_assemblies` `fc_top` on(((`exp_ec`.`id_exp_sfc` = `fc_top`.`id_exp_sfc`) and (`fc_top`.`location` = 'top')))) left join `flow_cell_assemblies` `fc_bottom` on(((`exp_ec`.`id_exp_sfc` = `fc_bottom`.`id_exp_sfc`) and (`fc_bottom`.`location` = 'bottom')))) left join `flow_electrolyte` `fe_top` on(((`exp_ec`.`id_exp_sfc` = `fe_top`.`id_exp_sfc`) and (`fe_top`.`location` = 'top')))) left join `flow_electrolyte` `fe_bottom` on(((`exp_ec`.`id_exp_sfc` = `fe_bottom`.`id_exp_sfc`) and (`fe_bottom`.`location` = 'bottom')))) left join `flow_gas` `fg_top_arring` on(((`exp_ec`.`id_exp_sfc` = `fg_top_arring`.`id_exp_sfc`) and (`fg_top_arring`.`location` = 'top') and (`fg_top_arring`.`function` = 'Arring')))) left join `flow_gas` `fg_top_purgevial` on(((`exp_ec`.`id_exp_sfc` = `fg_top_purgevial`.`id_exp_sfc`) and (`fg_top_purgevial`.`location` = 'top') and (`fg_top_purgevial`.`function` = 'purgevial')))) left join `flow_gas` `fg_top_main` on(((`exp_ec`.`id_exp_sfc` = `fg_top_main`.`id_exp_sfc`) and (`fg_top_main`.`location` = 'top') and (`fg_top_main`.`function` = 'main')))) left join `flow_gas` `fg_bottom_arring` on(((`exp_ec`.`id_exp_sfc` = `fg_bottom_arring`.`id_exp_sfc`) and (`fg_bottom_arring`.`location` = 'bottom') and (`fg_bottom_arring`.`function` = 'Arring')))) left join `flow_gas` `fg_bottom_purgevial` on(((`exp_ec`.`id_exp_sfc` = `fg_bottom_purgevial`.`id_exp_sfc`) and (`fg_bottom_purgevial`.`location` = 'bottom') and (`fg_bottom_purgevial`.`function` = 'purgevial')))) left join `flow_gas` `fg_bottom_main` on(((`exp_ec`.`id_exp_sfc` = `fg_bottom_main`.`id_exp_sfc`) and (`fg_bottom_main`.`location` = 'bottom') and (`fg_bottom_main`.`function` = 'main')))) left join `setups_sfc` `exp_sfc_name_setup_sfc` on((`exp_sfc`.`name_setup_sfc` = `exp_sfc_name_setup_sfc`.`name_setup_sfc`))) left join `reference_electrodes` `exp_ec_name_re` on((`exp_ec`.`name_RE` = `exp_ec_name_re`.`name_RE`))) left join `counter_electrodes` `exp_ec_name_ce` on((`exp_ec`.`name_CE` = `exp_ec_name_ce`.`name_CE`))) left join `flow_cells` `fc_top_name_flow_cell` on((`fc_top`.`name_flow_cell` = `fc_top_name_flow_cell`.`name_flow_cell`))) left join `sealings` `fc_top_id_sealing` on((`fc_top`.`id_sealing` = `fc_top_id_sealing`.`id_sealing`))) left join `porous_transport_layers` `fc_top_id_ptl` on((`fc_top`.`id_PTL` = `fc_top_id_ptl`.`id_PTL`))) left join `flow_cells` `fc_bottom_name_flow_cell` on((`fc_bottom`.`name_flow_cell` = `fc_bottom_name_flow_cell`.`name_flow_cell`))) left join `sealings` `fc_bottom_id_sealing` on((`fc_bottom`.`id_sealing` = `fc_bottom_id_sealing`.`id_sealing`))) left join `porous_transport_layers` `fc_bottom_id_ptl` on((`fc_bottom`.`id_PTL` = `fc_bottom_id_ptl`.`id_PTL`))) left join `peristaltic_pumps` `fe_top_id_pump_in` on((`fe_top`.`id_pump_in` = `fe_top_id_pump_in`.`id_pump`))) left join `peristaltic_tubings` `fe_top_id_tubing_in` on((`fe_top`.`id_tubing_in` = `fe_top_id_tubing_in`.`id_tubing`))) left join `peristaltic_pumps` `fe_top_id_pump_out` on((`fe_top`.`id_pump_out` = `fe_top_id_pump_out`.`id_pump`))) left join `peristaltic_tubings` `fe_top_id_tubing_out` on((`fe_top`.`id_tubing_out` = `fe_top_id_tubing_out`.`id_tubing`))) left join `peristaltic_pumps` `fe_bottom_id_pump_in` on((`fe_bottom`.`id_pump_in` = `fe_bottom_id_pump_in`.`id_pump`))) left join `peristaltic_tubings` `fe_bottom_id_tubing_in` on((`fe_bottom`.`id_tubing_in` = `fe_bottom_id_tubing_in`.`id_tubing`))) left join `peristaltic_pumps` `fe_bottom_id_pump_out` on((`fe_bottom`.`id_pump_out` = `fe_bottom_id_pump_out`.`id_pump`))) left join `peristaltic_tubings` `fe_bottom_id_tubing_out` on((`fe_bottom`.`id_tubing_out` = `fe_bottom_id_tubing_out`.`id_tubing`))) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `exp_ec_integration_expanded`
--

/*!50001 DROP VIEW IF EXISTS `exp_ec_integration_expanded`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `exp_ec_integration_expanded` AS select `ec_int`.`id_exp_ec_dataset` AS `id_exp_ec_dataset`,`ec_int`.`id_ana_integration_ec` AS `id_ana_integration_ec`,`ec_int`.`name_reaction` AS `name_reaction`,`ec_int`.`name_analysis` AS `name_analysis`,`ec_int`.`faradaic_efficiency__percent` AS `faradaic_efficiency__percent`,`exp_ec_datasets`.`name_exp_ec_dataset` AS `name_exp_ec_dataset`,`ec_reactions`.`name_product_of_interest` AS `name_product_of_interest`,`ec_reactions`.`number_electrons` AS `number_electrons`,`ana`.`id_data_integration_ec_baseline` AS `id_data_integration_ec_baseline`,`ana`.`id_data_integration_ec_begin` AS `id_data_integration_ec_begin`,`ana`.`id_data_integration_ec_end` AS `id_data_integration_ec_end`,`ana`.`t_integration_ec_baseline__timestamp` AS `t_integration_ec_baseline__timestamp`,`ana`.`t_integration_ec_begin__timestamp` AS `t_integration_ec_begin__timestamp`,`ana`.`t_integration_ec_end__timestamp` AS `t_integration_ec_end__timestamp`,`ana`.`Q_integrated_simps__C` AS `Q_integrated_simps__C`,`ana`.`Q_integrated_trapz__C` AS `Q_integrated_trapz__C`,`ana`.`I_offset__A` AS `I_offset__A`,`ana`.`no_of_datapoints_av_ec` AS `no_of_datapoints_av_ec`,`ana`.`no_of_datapoints_rolling_ec` AS `no_of_datapoints_rolling_ec`,`ana`.`auto_integration_ec` AS `auto_integration_ec`,`a`.`id_exp_sfc_first` AS `id_exp_sfc_first`,`exp_ec_expanded`.`id_exp_sfc` AS `id_exp_sfc`,`exp_ec_expanded`.`name_user` AS `name_user`,`exp_ec_expanded`.`name_setup_sfc` AS `name_setup_sfc`,`exp_ec_expanded`.`name_setup_sfc_alias` AS `name_setup_sfc_alias`,`exp_ec_expanded`.`name_setup_sfc_feature` AS `name_setup_sfc_feature`,`exp_ec_expanded`.`name_setup_sfc_type` AS `name_setup_sfc_type`,`exp_ec_expanded`.`t_start__timestamp` AS `t_start__timestamp`,`exp_ec_expanded`.`t_end__timestamp` AS `t_end__timestamp`,`exp_ec_expanded`.`rawdata_path` AS `rawdata_path`,`exp_ec_expanded`.`rawdata_computer` AS `rawdata_computer`,`exp_ec_expanded`.`id_ML` AS `id_ML`,`exp_ec_expanded`.`id_ML_technique` AS `id_ML_technique`,`exp_ec_expanded`.`id_sample` AS `id_sample`,`exp_ec_expanded`.`id_spot` AS `id_spot`,`exp_ec_expanded`.`force__N` AS `force__N`,`exp_ec_expanded`.`T_stage__degC` AS `T_stage__degC`,`exp_ec_expanded`.`interrupted` AS `interrupted`,`exp_ec_expanded`.`labview_sfc_version` AS `labview_sfc_version`,`exp_ec_expanded`.`db_version` AS `db_version`,`exp_ec_expanded`.`comment` AS `comment`,`exp_ec_expanded`.`ec_name_technique` AS `ec_name_technique`,`exp_ec_expanded`.`ec_R_u__ohm` AS `ec_R_u__ohm`,`exp_ec_expanded`.`ec_iR_corr_in_situ__percent` AS `ec_iR_corr_in_situ__percent`,`exp_ec_expanded`.`ec_R_u_determining_exp_ec` AS `ec_R_u_determining_exp_ec`,`exp_ec_expanded`.`ec_E_RE__VvsRHE` AS `ec_E_RE__VvsRHE`,`exp_ec_expanded`.`ec_name_RE` AS `ec_name_RE`,`exp_ec_expanded`.`ec_name_RE_material` AS `ec_name_RE_material`,`exp_ec_expanded`.`ec_name_RE_manufacturer` AS `ec_name_RE_manufacturer`,`exp_ec_expanded`.`ec_name_RE_model` AS `ec_name_RE_model`,`exp_ec_expanded`.`ec_name_CE` AS `ec_name_CE`,`exp_ec_expanded`.`ec_name_CE_material` AS `ec_name_CE_material`,`exp_ec_expanded`.`ec_name_CE_manufacturer` AS `ec_name_CE_manufacturer`,`exp_ec_expanded`.`ec_name_CE_model` AS `ec_name_CE_model`,`exp_ec_expanded`.`ec_name_device` AS `ec_name_device`,`exp_ec_expanded`.`ec_id_control_mode` AS `ec_id_control_mode`,`exp_ec_expanded`.`ec_id_ie_range` AS `ec_id_ie_range`,`exp_ec_expanded`.`ec_id_vch_range` AS `ec_id_vch_range`,`exp_ec_expanded`.`ec_id_ich_range` AS `ec_id_ich_range`,`exp_ec_expanded`.`ec_id_vch_filter` AS `ec_id_vch_filter`,`exp_ec_expanded`.`ec_id_ich_filter` AS `ec_id_ich_filter`,`exp_ec_expanded`.`ec_id_ca_speed` AS `ec_id_ca_speed`,`exp_ec_expanded`.`ec_id_ie_stability` AS `ec_id_ie_stability`,`exp_ec_expanded`.`ec_id_sampling_mode` AS `ec_id_sampling_mode`,`exp_ec_expanded`.`ec_ie_range_auto` AS `ec_ie_range_auto`,`exp_ec_expanded`.`ec_vch_range_auto` AS `ec_vch_range_auto`,`exp_ec_expanded`.`ec_ich_range_auto` AS `ec_ich_range_auto`,`exp_ec_expanded`.`samples_id_sample` AS `samples_id_sample`,`exp_ec_expanded`.`samples_name_sample` AS `samples_name_sample`,`exp_ec_expanded`.`samples_name_user` AS `samples_name_user`,`exp_ec_expanded`.`samples_t_manufactured__timestamp` AS `samples_t_manufactured__timestamp`,`exp_ec_expanded`.`samples_comment` AS `samples_comment`,`exp_ec_expanded`.`samples_total_loading__mg_cm2` AS `samples_total_loading__mg_cm2`,`exp_ec_expanded`.`spots_id_spot` AS `spots_id_spot`,`exp_ec_expanded`.`spots_spot_size__mm2` AS `spots_spot_size__mm2`,`exp_ec_expanded`.`spots_pos_x__mm` AS `spots_pos_x__mm`,`exp_ec_expanded`.`spots_pos_y__mm` AS `spots_pos_y__mm`,`exp_ec_expanded`.`spots_comment` AS `spots_comment`,`exp_ec_expanded`.`spots_total_loading__mg_cm2` AS `spots_total_loading__mg_cm2`,`exp_ec_expanded`.`cv_E_initial__VvsRE` AS `cv_E_initial__VvsRE`,`exp_ec_expanded`.`cv_E_apex1__VvsRE` AS `cv_E_apex1__VvsRE`,`exp_ec_expanded`.`cv_E_apex2__VvsRE` AS `cv_E_apex2__VvsRE`,`exp_ec_expanded`.`cv_E_final__VvsRE` AS `cv_E_final__VvsRE`,`exp_ec_expanded`.`cv_scanrate__mV_s` AS `cv_scanrate__mV_s`,`exp_ec_expanded`.`cv_stepsize__mV` AS `cv_stepsize__mV`,`exp_ec_expanded`.`cv_cycles` AS `cv_cycles`,`exp_ec_expanded`.`geis_f_initial__Hz` AS `geis_f_initial__Hz`,`exp_ec_expanded`.`geis_f_final__Hz` AS `geis_f_final__Hz`,`exp_ec_expanded`.`geis_I_dc__A` AS `geis_I_dc__A`,`exp_ec_expanded`.`geis_I_amplitude__A` AS `geis_I_amplitude__A`,`exp_ec_expanded`.`geis_R_initialguess__ohm` AS `geis_R_initialguess__ohm`,`exp_ec_expanded`.`geis_points_per_decade` AS `geis_points_per_decade`,`exp_ec_expanded`.`ghold_I_hold__A` AS `ghold_I_hold__A`,`exp_ec_expanded`.`ghold_t_hold__s` AS `ghold_t_hold__s`,`exp_ec_expanded`.`ghold_t_samplerate__s` AS `ghold_t_samplerate__s`,`exp_ec_expanded`.`peis_f_initial__Hz` AS `peis_f_initial__Hz`,`exp_ec_expanded`.`peis_f_final__Hz` AS `peis_f_final__Hz`,`exp_ec_expanded`.`peis_E_dc__VvsRE` AS `peis_E_dc__VvsRE`,`exp_ec_expanded`.`peis_E_amplitude__VvsRE` AS `peis_E_amplitude__VvsRE`,`exp_ec_expanded`.`peis_R_initialguess__ohm` AS `peis_R_initialguess__ohm`,`exp_ec_expanded`.`peis_points_per_decade` AS `peis_points_per_decade`,`exp_ec_expanded`.`phold_E_hold__VvsRE` AS `phold_E_hold__VvsRE`,`exp_ec_expanded`.`phold_t_hold__s` AS `phold_t_hold__s`,`exp_ec_expanded`.`phold_t_samplerate__s` AS `phold_t_samplerate__s`,`exp_ec_expanded`.`ppulse_E_hold1__VvsRE` AS `ppulse_E_hold1__VvsRE`,`exp_ec_expanded`.`ppulse_E_hold2__VvsRE` AS `ppulse_E_hold2__VvsRE`,`exp_ec_expanded`.`ppulse_t_hold1__s` AS `ppulse_t_hold1__s`,`exp_ec_expanded`.`ppulse_t_hold2__s` AS `ppulse_t_hold2__s`,`exp_ec_expanded`.`ppulse_t_samplerate__s` AS `ppulse_t_samplerate__s`,`exp_ec_expanded`.`ppulse_cycles` AS `ppulse_cycles`,`exp_ec_expanded`.`gpulse_I_hold1__A` AS `gpulse_I_hold1__A`,`exp_ec_expanded`.`gpulse_I_hold2__A` AS `gpulse_I_hold2__A`,`exp_ec_expanded`.`gpulse_t_hold1__s` AS `gpulse_t_hold1__s`,`exp_ec_expanded`.`gpulse_t_hold2__s` AS `gpulse_t_hold2__s`,`exp_ec_expanded`.`gpulse_t_samplerate__s` AS `gpulse_t_samplerate__s`,`exp_ec_expanded`.`gpulse_cycles` AS `gpulse_cycles`,`exp_ec_expanded`.`ramp_E_initial__VvsRE` AS `ramp_E_initial__VvsRE`,`exp_ec_expanded`.`ramp_E_final__VvsRE` AS `ramp_E_final__VvsRE`,`exp_ec_expanded`.`ramp_scanrate__mV_s` AS `ramp_scanrate__mV_s`,`exp_ec_expanded`.`ramp_stepsize__mV` AS `ramp_stepsize__mV`,`exp_ec_expanded`.`ramp_cycles` AS `ramp_cycles`,`exp_ec_expanded`.`fc_top_name_flow_cell` AS `fc_top_name_flow_cell`,`exp_ec_expanded`.`fc_top_name_flow_cell_name_user` AS `fc_top_name_flow_cell_name_user`,`exp_ec_expanded`.`fc_top_name_flow_cell_material` AS `fc_top_name_flow_cell_material`,`exp_ec_expanded`.`fc_top_name_flow_cell_A_opening_ideal__mm2` AS `fc_top_name_flow_cell_A_opening_ideal__mm2`,`exp_ec_expanded`.`fc_top_name_flow_cell_A_opening_real__mm2` AS `fc_top_name_flow_cell_A_opening_real__mm2`,`exp_ec_expanded`.`fc_top_name_flow_cell_manufacture_date` AS `fc_top_name_flow_cell_manufacture_date`,`exp_ec_expanded`.`fc_top_name_flow_cell_CAD_file` AS `fc_top_name_flow_cell_CAD_file`,`exp_ec_expanded`.`fc_top_name_flow_cell_comment` AS `fc_top_name_flow_cell_comment`,`exp_ec_expanded`.`fc_top_id_sealing` AS `fc_top_id_sealing`,`exp_ec_expanded`.`fc_top_id_sealing_name_user` AS `fc_top_id_sealing_name_user`,`exp_ec_expanded`.`fc_top_id_sealing_material` AS `fc_top_id_sealing_material`,`exp_ec_expanded`.`fc_top_id_sealing_A_sealing__mm2` AS `fc_top_id_sealing_A_sealing__mm2`,`exp_ec_expanded`.`fc_top_id_sealing_A_opening__mm2` AS `fc_top_id_sealing_A_opening__mm2`,`exp_ec_expanded`.`fc_top_id_sealing_thickness__mm` AS `fc_top_id_sealing_thickness__mm`,`exp_ec_expanded`.`fc_top_id_sealing_shaping_method` AS `fc_top_id_sealing_shaping_method`,`exp_ec_expanded`.`fc_top_id_sealing_comment` AS `fc_top_id_sealing_comment`,`exp_ec_expanded`.`fc_top_id_PTL` AS `fc_top_id_PTL`,`exp_ec_expanded`.`fc_top_id_PTL_name_user` AS `fc_top_id_PTL_name_user`,`exp_ec_expanded`.`fc_top_id_PTL_material` AS `fc_top_id_PTL_material`,`exp_ec_expanded`.`fc_top_id_PTL_thickness__mm` AS `fc_top_id_PTL_thickness__mm`,`exp_ec_expanded`.`fc_top_id_PTL_manufacturer` AS `fc_top_id_PTL_manufacturer`,`exp_ec_expanded`.`fc_top_id_PTL_A_PTL__mm2` AS `fc_top_id_PTL_A_PTL__mm2`,`exp_ec_expanded`.`fc_top_id_PTL_shaping_method` AS `fc_top_id_PTL_shaping_method`,`exp_ec_expanded`.`fc_top_id_PTL_comment` AS `fc_top_id_PTL_comment`,`exp_ec_expanded`.`fc_bottom_name_flow_cell` AS `fc_bottom_name_flow_cell`,`exp_ec_expanded`.`fc_bottom_name_flow_cell_name_user` AS `fc_bottom_name_flow_cell_name_user`,`exp_ec_expanded`.`fc_bottom_name_flow_cell_material` AS `fc_bottom_name_flow_cell_material`,`exp_ec_expanded`.`fc_bottom_name_flow_cell_A_opening_ideal__mm2` AS `fc_bottom_name_flow_cell_A_opening_ideal__mm2`,`exp_ec_expanded`.`fc_bottom_name_flow_cell_A_opening_real__mm2` AS `fc_bottom_name_flow_cell_A_opening_real__mm2`,`exp_ec_expanded`.`fc_bottom_name_flow_cell_manufacture_date` AS `fc_bottom_name_flow_cell_manufacture_date`,`exp_ec_expanded`.`fc_bottom_name_flow_cell_CAD_file` AS `fc_bottom_name_flow_cell_CAD_file`,`exp_ec_expanded`.`fc_bottom_name_flow_cell_comment` AS `fc_bottom_name_flow_cell_comment`,`exp_ec_expanded`.`fc_bottom_id_sealing` AS `fc_bottom_id_sealing`,`exp_ec_expanded`.`fc_bottom_id_sealing_name_user` AS `fc_bottom_id_sealing_name_user`,`exp_ec_expanded`.`fc_bottom_id_sealing_material` AS `fc_bottom_id_sealing_material`,`exp_ec_expanded`.`fc_bottom_id_sealing_A_sealing__mm2` AS `fc_bottom_id_sealing_A_sealing__mm2`,`exp_ec_expanded`.`fc_bottom_id_sealing_A_opening__mm2` AS `fc_bottom_id_sealing_A_opening__mm2`,`exp_ec_expanded`.`fc_bottom_id_sealing_thickness__mm` AS `fc_bottom_id_sealing_thickness__mm`,`exp_ec_expanded`.`fc_bottom_id_sealing_shaping_method` AS `fc_bottom_id_sealing_shaping_method`,`exp_ec_expanded`.`fc_bottom_id_sealing_comment` AS `fc_bottom_id_sealing_comment`,`exp_ec_expanded`.`fc_bottom_id_PTL` AS `fc_bottom_id_PTL`,`exp_ec_expanded`.`fc_bottom_id_PTL_name_user` AS `fc_bottom_id_PTL_name_user`,`exp_ec_expanded`.`fc_bottom_id_PTL_material` AS `fc_bottom_id_PTL_material`,`exp_ec_expanded`.`fc_bottom_id_PTL_thickness__mm` AS `fc_bottom_id_PTL_thickness__mm`,`exp_ec_expanded`.`fc_bottom_id_PTL_manufacturer` AS `fc_bottom_id_PTL_manufacturer`,`exp_ec_expanded`.`fc_bottom_id_PTL_A_PTL__mm2` AS `fc_bottom_id_PTL_A_PTL__mm2`,`exp_ec_expanded`.`fc_bottom_id_PTL_shaping_method` AS `fc_bottom_id_PTL_shaping_method`,`exp_ec_expanded`.`fc_bottom_id_PTL_comment` AS `fc_bottom_id_PTL_comment`,`exp_ec_expanded`.`fe_top_id_pump_in` AS `fe_top_id_pump_in`,`exp_ec_expanded`.`fe_top_id_pump_in_manufacturer` AS `fe_top_id_pump_in_manufacturer`,`exp_ec_expanded`.`fe_top_id_pump_in_model` AS `fe_top_id_pump_in_model`,`exp_ec_expanded`.`fe_top_id_pump_in_device` AS `fe_top_id_pump_in_device`,`exp_ec_expanded`.`fe_top_id_tubing_in` AS `fe_top_id_tubing_in`,`exp_ec_expanded`.`fe_top_id_tubing_in_name_tubing` AS `fe_top_id_tubing_in_name_tubing`,`exp_ec_expanded`.`fe_top_id_tubing_in_inner_diameter__mm` AS `fe_top_id_tubing_in_inner_diameter__mm`,`exp_ec_expanded`.`fe_top_id_tubing_in_color_code` AS `fe_top_id_tubing_in_color_code`,`exp_ec_expanded`.`fe_top_id_tubing_in_manufacturer` AS `fe_top_id_tubing_in_manufacturer`,`exp_ec_expanded`.`fe_top_id_tubing_in_model` AS `fe_top_id_tubing_in_model`,`exp_ec_expanded`.`fe_top_pump_rate_in__rpm` AS `fe_top_pump_rate_in__rpm`,`exp_ec_expanded`.`fe_top_id_pump_out` AS `fe_top_id_pump_out`,`exp_ec_expanded`.`fe_top_id_pump_out_manufacturer` AS `fe_top_id_pump_out_manufacturer`,`exp_ec_expanded`.`fe_top_id_pump_out_model` AS `fe_top_id_pump_out_model`,`exp_ec_expanded`.`fe_top_id_pump_out_device` AS `fe_top_id_pump_out_device`,`exp_ec_expanded`.`fe_top_id_tubing_out` AS `fe_top_id_tubing_out`,`exp_ec_expanded`.`fe_top_id_tubing_out_name_tubing` AS `fe_top_id_tubing_out_name_tubing`,`exp_ec_expanded`.`fe_top_id_tubing_out_inner_diameter__mm` AS `fe_top_id_tubing_out_inner_diameter__mm`,`exp_ec_expanded`.`fe_top_id_tubing_out_color_code` AS `fe_top_id_tubing_out_color_code`,`exp_ec_expanded`.`fe_top_id_tubing_out_manufacturer` AS `fe_top_id_tubing_out_manufacturer`,`exp_ec_expanded`.`fe_top_id_tubing_out_model` AS `fe_top_id_tubing_out_model`,`exp_ec_expanded`.`fe_top_pump_rate_out__rpm` AS `fe_top_pump_rate_out__rpm`,`exp_ec_expanded`.`fe_top_flow_rate_real__mul_min` AS `fe_top_flow_rate_real__mul_min`,`exp_ec_expanded`.`fe_top_name_electrolyte` AS `fe_top_name_electrolyte`,`exp_ec_expanded`.`fe_top_c_electrolyte__mol_L` AS `fe_top_c_electrolyte__mol_L`,`exp_ec_expanded`.`fe_top_T_electrolyte__degC` AS `fe_top_T_electrolyte__degC`,`exp_ec_expanded`.`fe_bottom_id_pump_in` AS `fe_bottom_id_pump_in`,`exp_ec_expanded`.`fe_bottom_id_pump_in_manufacturer` AS `fe_bottom_id_pump_in_manufacturer`,`exp_ec_expanded`.`fe_bottom_id_pump_in_model` AS `fe_bottom_id_pump_in_model`,`exp_ec_expanded`.`fe_bottom_id_pump_in_device` AS `fe_bottom_id_pump_in_device`,`exp_ec_expanded`.`fe_bottom_id_tubing_in` AS `fe_bottom_id_tubing_in`,`exp_ec_expanded`.`fe_bottom_id_tubing_in_name_tubing` AS `fe_bottom_id_tubing_in_name_tubing`,`exp_ec_expanded`.`fe_bottom_id_tubing_in_inner_diameter__mm` AS `fe_bottom_id_tubing_in_inner_diameter__mm`,`exp_ec_expanded`.`fe_bottom_id_tubing_in_color_code` AS `fe_bottom_id_tubing_in_color_code`,`exp_ec_expanded`.`fe_bottom_id_tubing_in_manufacturer` AS `fe_bottom_id_tubing_in_manufacturer`,`exp_ec_expanded`.`fe_bottom_id_tubing_in_model` AS `fe_bottom_id_tubing_in_model`,`exp_ec_expanded`.`fe_bottom_pump_rate_in__rpm` AS `fe_bottom_pump_rate_in__rpm`,`exp_ec_expanded`.`fe_bottom_id_pump_out` AS `fe_bottom_id_pump_out`,`exp_ec_expanded`.`fe_bottom_id_pump_out_manufacturer` AS `fe_bottom_id_pump_out_manufacturer`,`exp_ec_expanded`.`fe_bottom_id_pump_out_model` AS `fe_bottom_id_pump_out_model`,`exp_ec_expanded`.`fe_bottom_id_pump_out_device` AS `fe_bottom_id_pump_out_device`,`exp_ec_expanded`.`fe_bottom_id_tubing_out` AS `fe_bottom_id_tubing_out`,`exp_ec_expanded`.`fe_bottom_id_tubing_out_name_tubing` AS `fe_bottom_id_tubing_out_name_tubing`,`exp_ec_expanded`.`fe_bottom_id_tubing_out_inner_diameter__mm` AS `fe_bottom_id_tubing_out_inner_diameter__mm`,`exp_ec_expanded`.`fe_bottom_id_tubing_out_color_code` AS `fe_bottom_id_tubing_out_color_code`,`exp_ec_expanded`.`fe_bottom_id_tubing_out_manufacturer` AS `fe_bottom_id_tubing_out_manufacturer`,`exp_ec_expanded`.`fe_bottom_id_tubing_out_model` AS `fe_bottom_id_tubing_out_model`,`exp_ec_expanded`.`fe_bottom_pump_rate_out__rpm` AS `fe_bottom_pump_rate_out__rpm`,`exp_ec_expanded`.`fe_bottom_flow_rate_real__mul_min` AS `fe_bottom_flow_rate_real__mul_min`,`exp_ec_expanded`.`fe_bottom_name_electrolyte` AS `fe_bottom_name_electrolyte`,`exp_ec_expanded`.`fe_bottom_c_electrolyte__mol_L` AS `fe_bottom_c_electrolyte__mol_L`,`exp_ec_expanded`.`fe_bottom_T_electrolyte__degC` AS `fe_bottom_T_electrolyte__degC`,`exp_ec_expanded`.`fg_top_Arring_name_gas` AS `fg_top_Arring_name_gas`,`exp_ec_expanded`.`fg_top_Arring_flow_rate__mL_min` AS `fg_top_Arring_flow_rate__mL_min`,`exp_ec_expanded`.`fg_top_purgevial_name_gas` AS `fg_top_purgevial_name_gas`,`exp_ec_expanded`.`fg_top_purgevial_flow_rate__mL_min` AS `fg_top_purgevial_flow_rate__mL_min`,`exp_ec_expanded`.`fg_top_main_name_gas` AS `fg_top_main_name_gas`,`exp_ec_expanded`.`fg_top_main_flow_rate__mL_min` AS `fg_top_main_flow_rate__mL_min`,`exp_ec_expanded`.`fg_bottom_Arring_name_gas` AS `fg_bottom_Arring_name_gas`,`exp_ec_expanded`.`fg_bottom_Arring_flow_rate__mL_min` AS `fg_bottom_Arring_flow_rate__mL_min`,`exp_ec_expanded`.`fg_bottom_purgevial_name_gas` AS `fg_bottom_purgevial_name_gas`,`exp_ec_expanded`.`fg_bottom_purgevial_flow_rate__mL_min` AS `fg_bottom_purgevial_flow_rate__mL_min`,`exp_ec_expanded`.`fg_bottom_main_name_gas` AS `fg_bottom_main_name_gas`,`exp_ec_expanded`.`fg_bottom_main_flow_rate__mL_min` AS `fg_bottom_main_flow_rate__mL_min`,(((`ana`.`Q_integrated_simps__C` / (`ec_reactions`.`number_electrons` * 96485.33212)) * `ec_int`.`faradaic_efficiency__percent`) / 100) AS `n_product_of_interest_simps__mol`,(((`ana`.`Q_integrated_trapz__C` / (`ec_reactions`.`number_electrons` * 96485.33212)) * `ec_int`.`faradaic_efficiency__percent`) / 100) AS `n_product_of_interest_trapz__mol` from ((((((select `exp_ec_integration`.`id_exp_ec_dataset` AS `id_exp_ec_dataset`,`exp_ec_integration`.`name_analysis` AS `name_analysis`,`exp_ec_integration`.`id_ana_integration` AS `id_ana_integration_ec`,`exp_ec_integration`.`name_reaction` AS `name_reaction`,`exp_ec_integration`.`faradaic_efficiency__percent` AS `faradaic_efficiency__percent` from `exp_ec_integration`) `ec_int` left join `exp_ec_datasets` on((`ec_int`.`id_exp_ec_dataset` = `exp_ec_datasets`.`id_exp_ec_dataset`))) left join `ec_reactions` on((`ec_int`.`name_reaction` = `ec_reactions`.`name_reaction`))) left join (select `ana_integrations`.`id_ana_integration` AS `id_ana_integration_ec`,`ana_integrations`.`id_data_integration_baseline` AS `id_data_integration_ec_baseline`,`ana_integrations`.`id_data_integration_begin` AS `id_data_integration_ec_begin`,`ana_integrations`.`id_data_integration_end` AS `id_data_integration_ec_end`,`ana_integrations`.`t_integration_baseline__timestamp` AS `t_integration_ec_baseline__timestamp`,`ana_integrations`.`t_integration_begin__timestamp` AS `t_integration_ec_begin__timestamp`,`ana_integrations`.`t_integration_end__timestamp` AS `t_integration_ec_end__timestamp`,`ana_integrations`.`area_integrated_simps` AS `Q_integrated_simps__C`,`ana_integrations`.`area_integrated_trapz` AS `Q_integrated_trapz__C`,`ana_integrations`.`y_offset` AS `I_offset__A`,`ana_integrations`.`no_of_datapoints_avg` AS `no_of_datapoints_av_ec`,`ana_integrations`.`no_of_datapoints_rolling` AS `no_of_datapoints_rolling_ec`,`ana_integrations`.`auto_integration` AS `auto_integration_ec` from `ana_integrations`) `ana` on((`ec_int`.`id_ana_integration_ec` = `ana`.`id_ana_integration_ec`))) left join (select `exp_ec_datasets_definer`.`id_exp_ec_dataset` AS `id_exp_ec_dataset`,min(`exp_ec_datasets_definer`.`id_exp_sfc`) AS `id_exp_sfc_first` from `exp_ec_datasets_definer` group by `exp_ec_datasets_definer`.`id_exp_ec_dataset`) `a` on((`ec_int`.`id_exp_ec_dataset` = `a`.`id_exp_ec_dataset`))) left join `exp_ec_expanded` on((`a`.`id_exp_sfc_first` = `exp_ec_expanded`.`id_exp_sfc`))) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `exp_ec_polcurve_expanded`
--

/*!50001 DROP VIEW IF EXISTS `exp_ec_polcurve_expanded`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `exp_ec_polcurve_expanded` AS select `exp_ec_polcurve`.`id_exp_ec_polcurve` AS `id_exp_ec_polcurve`,`exp_ec_polcurve`.`number_datapoints_in_tail` AS `number_datapoints_in_tail`,`exp_ec_polcurve`.`changed_exp_parameters` AS `changed_exp_parameters`,`exp_ec_polcurve`.`t_inserted_data__timestamp` AS `t_inserted_data__timestamp`,`exp_ec_polcurve`.`file_path_processing_plot` AS `file_path_processing_plot`,`a`.`id_exp_sfc_ghold_first` AS `id_exp_sfc_ghold_first`,`a`.`id_exp_sfc_geis_first` AS `id_exp_sfc_geis_first`,`e`.`id_exp_sfc` AS `id_exp_sfc`,`e`.`name_user` AS `name_user`,`e`.`name_setup_sfc` AS `name_setup_sfc`,`e`.`name_setup_sfc_alias` AS `name_setup_sfc_alias`,`e`.`name_setup_sfc_feature` AS `name_setup_sfc_feature`,`e`.`name_setup_sfc_type` AS `name_setup_sfc_type`,`e`.`t_start__timestamp` AS `t_start__timestamp`,`e`.`rawdata_path` AS `rawdata_path`,`e`.`rawdata_computer` AS `rawdata_computer`,`e`.`id_ML` AS `id_ML`,`e`.`id_ML_technique` AS `id_ML_technique`,`e`.`id_sample` AS `id_sample`,`e`.`id_spot` AS `id_spot`,`e`.`force__N` AS `force__N`,`e`.`T_stage__degC` AS `T_stage__degC`,`e`.`interrupted` AS `interrupted`,`e`.`labview_sfc_version` AS `labview_sfc_version`,`e`.`db_version` AS `db_version`,`e`.`comment` AS `comment`,`e`.`t_end__timestamp` AS `t_end__timestamp`,`e`.`ec_name_technique` AS `ec_name_technique`,`e`.`ec_R_u__ohm` AS `ec_R_u__ohm`,`e`.`ec_iR_corr_in_situ__percent` AS `ec_iR_corr_in_situ__percent`,`e`.`ec_R_u_determining_exp_ec` AS `ec_R_u_determining_exp_ec`,`e`.`ec_E_RE__VvsRHE` AS `ec_E_RE__VvsRHE`,`e`.`ec_name_RE` AS `ec_name_RE`,`e`.`ec_name_RE_material` AS `ec_name_RE_material`,`e`.`ec_name_RE_manufacturer` AS `ec_name_RE_manufacturer`,`e`.`ec_name_RE_model` AS `ec_name_RE_model`,`e`.`ec_name_CE` AS `ec_name_CE`,`e`.`ec_name_CE_material` AS `ec_name_CE_material`,`e`.`ec_name_CE_manufacturer` AS `ec_name_CE_manufacturer`,`e`.`ec_name_CE_model` AS `ec_name_CE_model`,`e`.`ec_name_device` AS `ec_name_device`,`e`.`ec_id_control_mode` AS `ec_id_control_mode`,`e`.`ec_id_ie_range` AS `ec_id_ie_range`,`e`.`ec_id_vch_range` AS `ec_id_vch_range`,`e`.`ec_id_ich_range` AS `ec_id_ich_range`,`e`.`ec_id_vch_filter` AS `ec_id_vch_filter`,`e`.`ec_id_ich_filter` AS `ec_id_ich_filter`,`e`.`ec_id_ca_speed` AS `ec_id_ca_speed`,`e`.`ec_id_ie_stability` AS `ec_id_ie_stability`,`e`.`ec_id_sampling_mode` AS `ec_id_sampling_mode`,`e`.`ec_ie_range_auto` AS `ec_ie_range_auto`,`e`.`ec_vch_range_auto` AS `ec_vch_range_auto`,`e`.`ec_ich_range_auto` AS `ec_ich_range_auto`,`e`.`samples_id_sample` AS `samples_id_sample`,`e`.`samples_name_sample` AS `samples_name_sample`,`e`.`samples_name_user` AS `samples_name_user`,`e`.`samples_t_manufactured__timestamp` AS `samples_t_manufactured__timestamp`,`e`.`samples_comment` AS `samples_comment`,`e`.`samples_total_loading__mg_cm2` AS `samples_total_loading__mg_cm2`,`e`.`spots_id_spot` AS `spots_id_spot`,`e`.`spots_spot_size__mm2` AS `spots_spot_size__mm2`,`e`.`spots_pos_x__mm` AS `spots_pos_x__mm`,`e`.`spots_pos_y__mm` AS `spots_pos_y__mm`,`e`.`spots_comment` AS `spots_comment`,`e`.`spots_total_loading__mg_cm2` AS `spots_total_loading__mg_cm2`,`e`.`cv_E_initial__VvsRE` AS `cv_E_initial__VvsRE`,`e`.`cv_E_apex1__VvsRE` AS `cv_E_apex1__VvsRE`,`e`.`cv_E_apex2__VvsRE` AS `cv_E_apex2__VvsRE`,`e`.`cv_E_final__VvsRE` AS `cv_E_final__VvsRE`,`e`.`cv_scanrate__mV_s` AS `cv_scanrate__mV_s`,`e`.`cv_stepsize__mV` AS `cv_stepsize__mV`,`e`.`cv_cycles` AS `cv_cycles`,`e`.`ghold_I_hold__A` AS `ghold_I_hold__A`,`e`.`ghold_t_hold__s` AS `ghold_t_hold__s`,`e`.`ghold_t_samplerate__s` AS `ghold_t_samplerate__s`,`e`.`peis_f_initial__Hz` AS `peis_f_initial__Hz`,`e`.`peis_f_final__Hz` AS `peis_f_final__Hz`,`e`.`peis_E_dc__VvsRE` AS `peis_E_dc__VvsRE`,`e`.`peis_E_amplitude__VvsRE` AS `peis_E_amplitude__VvsRE`,`e`.`peis_R_initialguess__ohm` AS `peis_R_initialguess__ohm`,`e`.`peis_points_per_decade` AS `peis_points_per_decade`,`e`.`phold_E_hold__VvsRE` AS `phold_E_hold__VvsRE`,`e`.`phold_t_hold__s` AS `phold_t_hold__s`,`e`.`phold_t_samplerate__s` AS `phold_t_samplerate__s`,`e`.`ppulse_E_hold1__VvsRE` AS `ppulse_E_hold1__VvsRE`,`e`.`ppulse_E_hold2__VvsRE` AS `ppulse_E_hold2__VvsRE`,`e`.`ppulse_t_hold1__s` AS `ppulse_t_hold1__s`,`e`.`ppulse_t_hold2__s` AS `ppulse_t_hold2__s`,`e`.`ppulse_t_samplerate__s` AS `ppulse_t_samplerate__s`,`e`.`ppulse_cycles` AS `ppulse_cycles`,`e`.`gpulse_I_hold1__A` AS `gpulse_I_hold1__A`,`e`.`gpulse_I_hold2__A` AS `gpulse_I_hold2__A`,`e`.`gpulse_t_hold1__s` AS `gpulse_t_hold1__s`,`e`.`gpulse_t_hold2__s` AS `gpulse_t_hold2__s`,`e`.`gpulse_t_samplerate__s` AS `gpulse_t_samplerate__s`,`e`.`gpulse_cycles` AS `gpulse_cycles`,`e`.`ramp_E_initial__VvsRE` AS `ramp_E_initial__VvsRE`,`e`.`ramp_E_final__VvsRE` AS `ramp_E_final__VvsRE`,`e`.`ramp_scanrate__mV_s` AS `ramp_scanrate__mV_s`,`e`.`ramp_stepsize__mV` AS `ramp_stepsize__mV`,`e`.`ramp_cycles` AS `ramp_cycles`,`e`.`fc_top_name_flow_cell` AS `fc_top_name_flow_cell`,`e`.`fc_top_name_flow_cell_name_user` AS `fc_top_name_flow_cell_name_user`,`e`.`fc_top_name_flow_cell_material` AS `fc_top_name_flow_cell_material`,`e`.`fc_top_name_flow_cell_A_opening_ideal__mm2` AS `fc_top_name_flow_cell_A_opening_ideal__mm2`,`e`.`fc_top_name_flow_cell_A_opening_real__mm2` AS `fc_top_name_flow_cell_A_opening_real__mm2`,`e`.`fc_top_name_flow_cell_manufacture_date` AS `fc_top_name_flow_cell_manufacture_date`,`e`.`fc_top_name_flow_cell_CAD_file` AS `fc_top_name_flow_cell_CAD_file`,`e`.`fc_top_name_flow_cell_comment` AS `fc_top_name_flow_cell_comment`,`e`.`fc_top_id_sealing` AS `fc_top_id_sealing`,`e`.`fc_top_id_sealing_name_user` AS `fc_top_id_sealing_name_user`,`e`.`fc_top_id_sealing_material` AS `fc_top_id_sealing_material`,`e`.`fc_top_id_sealing_A_sealing__mm2` AS `fc_top_id_sealing_A_sealing__mm2`,`e`.`fc_top_id_sealing_A_opening__mm2` AS `fc_top_id_sealing_A_opening__mm2`,`e`.`fc_top_id_sealing_thickness__mm` AS `fc_top_id_sealing_thickness__mm`,`e`.`fc_top_id_sealing_shaping_method` AS `fc_top_id_sealing_shaping_method`,`e`.`fc_top_id_sealing_comment` AS `fc_top_id_sealing_comment`,`e`.`fc_top_id_PTL` AS `fc_top_id_PTL`,`e`.`fc_top_id_PTL_name_user` AS `fc_top_id_PTL_name_user`,`e`.`fc_top_id_PTL_material` AS `fc_top_id_PTL_material`,`e`.`fc_top_id_PTL_thickness__mm` AS `fc_top_id_PTL_thickness__mm`,`e`.`fc_top_id_PTL_manufacturer` AS `fc_top_id_PTL_manufacturer`,`e`.`fc_top_id_PTL_A_PTL__mm2` AS `fc_top_id_PTL_A_PTL__mm2`,`e`.`fc_top_id_PTL_shaping_method` AS `fc_top_id_PTL_shaping_method`,`e`.`fc_top_id_PTL_comment` AS `fc_top_id_PTL_comment`,`e`.`fc_bottom_name_flow_cell` AS `fc_bottom_name_flow_cell`,`e`.`fc_bottom_name_flow_cell_name_user` AS `fc_bottom_name_flow_cell_name_user`,`e`.`fc_bottom_name_flow_cell_material` AS `fc_bottom_name_flow_cell_material`,`e`.`fc_bottom_name_flow_cell_A_opening_ideal__mm2` AS `fc_bottom_name_flow_cell_A_opening_ideal__mm2`,`e`.`fc_bottom_name_flow_cell_A_opening_real__mm2` AS `fc_bottom_name_flow_cell_A_opening_real__mm2`,`e`.`fc_bottom_name_flow_cell_manufacture_date` AS `fc_bottom_name_flow_cell_manufacture_date`,`e`.`fc_bottom_name_flow_cell_CAD_file` AS `fc_bottom_name_flow_cell_CAD_file`,`e`.`fc_bottom_name_flow_cell_comment` AS `fc_bottom_name_flow_cell_comment`,`e`.`fc_bottom_id_sealing` AS `fc_bottom_id_sealing`,`e`.`fc_bottom_id_sealing_name_user` AS `fc_bottom_id_sealing_name_user`,`e`.`fc_bottom_id_sealing_material` AS `fc_bottom_id_sealing_material`,`e`.`fc_bottom_id_sealing_A_sealing__mm2` AS `fc_bottom_id_sealing_A_sealing__mm2`,`e`.`fc_bottom_id_sealing_A_opening__mm2` AS `fc_bottom_id_sealing_A_opening__mm2`,`e`.`fc_bottom_id_sealing_thickness__mm` AS `fc_bottom_id_sealing_thickness__mm`,`e`.`fc_bottom_id_sealing_shaping_method` AS `fc_bottom_id_sealing_shaping_method`,`e`.`fc_bottom_id_sealing_comment` AS `fc_bottom_id_sealing_comment`,`e`.`fc_bottom_id_PTL` AS `fc_bottom_id_PTL`,`e`.`fc_bottom_id_PTL_name_user` AS `fc_bottom_id_PTL_name_user`,`e`.`fc_bottom_id_PTL_material` AS `fc_bottom_id_PTL_material`,`e`.`fc_bottom_id_PTL_thickness__mm` AS `fc_bottom_id_PTL_thickness__mm`,`e`.`fc_bottom_id_PTL_manufacturer` AS `fc_bottom_id_PTL_manufacturer`,`e`.`fc_bottom_id_PTL_A_PTL__mm2` AS `fc_bottom_id_PTL_A_PTL__mm2`,`e`.`fc_bottom_id_PTL_shaping_method` AS `fc_bottom_id_PTL_shaping_method`,`e`.`fc_bottom_id_PTL_comment` AS `fc_bottom_id_PTL_comment`,`e`.`fe_top_id_pump_in` AS `fe_top_id_pump_in`,`e`.`fe_top_id_pump_in_manufacturer` AS `fe_top_id_pump_in_manufacturer`,`e`.`fe_top_id_pump_in_model` AS `fe_top_id_pump_in_model`,`e`.`fe_top_id_pump_in_device` AS `fe_top_id_pump_in_device`,`e`.`fe_top_id_tubing_in` AS `fe_top_id_tubing_in`,`e`.`fe_top_id_tubing_in_name_tubing` AS `fe_top_id_tubing_in_name_tubing`,`e`.`fe_top_id_tubing_in_inner_diameter__mm` AS `fe_top_id_tubing_in_inner_diameter__mm`,`e`.`fe_top_id_tubing_in_color_code` AS `fe_top_id_tubing_in_color_code`,`e`.`fe_top_id_tubing_in_manufacturer` AS `fe_top_id_tubing_in_manufacturer`,`e`.`fe_top_id_tubing_in_model` AS `fe_top_id_tubing_in_model`,`e`.`fe_top_pump_rate_in__rpm` AS `fe_top_pump_rate_in__rpm`,`e`.`fe_top_id_pump_out` AS `fe_top_id_pump_out`,`e`.`fe_top_id_pump_out_manufacturer` AS `fe_top_id_pump_out_manufacturer`,`e`.`fe_top_id_pump_out_model` AS `fe_top_id_pump_out_model`,`e`.`fe_top_id_pump_out_device` AS `fe_top_id_pump_out_device`,`e`.`fe_top_id_tubing_out` AS `fe_top_id_tubing_out`,`e`.`fe_top_id_tubing_out_name_tubing` AS `fe_top_id_tubing_out_name_tubing`,`e`.`fe_top_id_tubing_out_inner_diameter__mm` AS `fe_top_id_tubing_out_inner_diameter__mm`,`e`.`fe_top_id_tubing_out_color_code` AS `fe_top_id_tubing_out_color_code`,`e`.`fe_top_id_tubing_out_manufacturer` AS `fe_top_id_tubing_out_manufacturer`,`e`.`fe_top_id_tubing_out_model` AS `fe_top_id_tubing_out_model`,`e`.`fe_top_pump_rate_out__rpm` AS `fe_top_pump_rate_out__rpm`,`e`.`fe_top_flow_rate_real__mul_min` AS `fe_top_flow_rate_real__mul_min`,`e`.`fe_top_name_electrolyte` AS `fe_top_name_electrolyte`,`e`.`fe_top_c_electrolyte__mol_L` AS `fe_top_c_electrolyte__mol_L`,`e`.`fe_top_T_electrolyte__degC` AS `fe_top_T_electrolyte__degC`,`e`.`fe_bottom_id_pump_in` AS `fe_bottom_id_pump_in`,`e`.`fe_bottom_id_pump_in_manufacturer` AS `fe_bottom_id_pump_in_manufacturer`,`e`.`fe_bottom_id_pump_in_model` AS `fe_bottom_id_pump_in_model`,`e`.`fe_bottom_id_pump_in_device` AS `fe_bottom_id_pump_in_device`,`e`.`fe_bottom_id_tubing_in` AS `fe_bottom_id_tubing_in`,`e`.`fe_bottom_id_tubing_in_name_tubing` AS `fe_bottom_id_tubing_in_name_tubing`,`e`.`fe_bottom_id_tubing_in_inner_diameter__mm` AS `fe_bottom_id_tubing_in_inner_diameter__mm`,`e`.`fe_bottom_id_tubing_in_color_code` AS `fe_bottom_id_tubing_in_color_code`,`e`.`fe_bottom_id_tubing_in_manufacturer` AS `fe_bottom_id_tubing_in_manufacturer`,`e`.`fe_bottom_id_tubing_in_model` AS `fe_bottom_id_tubing_in_model`,`e`.`fe_bottom_pump_rate_in__rpm` AS `fe_bottom_pump_rate_in__rpm`,`e`.`fe_bottom_id_pump_out` AS `fe_bottom_id_pump_out`,`e`.`fe_bottom_id_pump_out_manufacturer` AS `fe_bottom_id_pump_out_manufacturer`,`e`.`fe_bottom_id_pump_out_model` AS `fe_bottom_id_pump_out_model`,`e`.`fe_bottom_id_pump_out_device` AS `fe_bottom_id_pump_out_device`,`e`.`fe_bottom_id_tubing_out` AS `fe_bottom_id_tubing_out`,`e`.`fe_bottom_id_tubing_out_name_tubing` AS `fe_bottom_id_tubing_out_name_tubing`,`e`.`fe_bottom_id_tubing_out_inner_diameter__mm` AS `fe_bottom_id_tubing_out_inner_diameter__mm`,`e`.`fe_bottom_id_tubing_out_color_code` AS `fe_bottom_id_tubing_out_color_code`,`e`.`fe_bottom_id_tubing_out_manufacturer` AS `fe_bottom_id_tubing_out_manufacturer`,`e`.`fe_bottom_id_tubing_out_model` AS `fe_bottom_id_tubing_out_model`,`e`.`fe_bottom_pump_rate_out__rpm` AS `fe_bottom_pump_rate_out__rpm`,`e`.`fe_bottom_flow_rate_real__mul_min` AS `fe_bottom_flow_rate_real__mul_min`,`e`.`fe_bottom_name_electrolyte` AS `fe_bottom_name_electrolyte`,`e`.`fe_bottom_c_electrolyte__mol_L` AS `fe_bottom_c_electrolyte__mol_L`,`e`.`fe_bottom_T_electrolyte__degC` AS `fe_bottom_T_electrolyte__degC`,`e`.`fg_top_Arring_name_gas` AS `fg_top_Arring_name_gas`,`e`.`fg_top_Arring_flow_rate__mL_min` AS `fg_top_Arring_flow_rate__mL_min`,`e`.`fg_top_purgevial_name_gas` AS `fg_top_purgevial_name_gas`,`e`.`fg_top_purgevial_flow_rate__mL_min` AS `fg_top_purgevial_flow_rate__mL_min`,`e`.`fg_top_main_name_gas` AS `fg_top_main_name_gas`,`e`.`fg_top_main_flow_rate__mL_min` AS `fg_top_main_flow_rate__mL_min`,`e`.`fg_bottom_Arring_name_gas` AS `fg_bottom_Arring_name_gas`,`e`.`fg_bottom_Arring_flow_rate__mL_min` AS `fg_bottom_Arring_flow_rate__mL_min`,`e`.`fg_bottom_purgevial_name_gas` AS `fg_bottom_purgevial_name_gas`,`e`.`fg_bottom_purgevial_flow_rate__mL_min` AS `fg_bottom_purgevial_flow_rate__mL_min`,`e`.`fg_bottom_main_name_gas` AS `fg_bottom_main_name_gas`,`e`.`fg_bottom_main_flow_rate__mL_min` AS `fg_bottom_main_flow_rate__mL_min`,`g`.`id_exp_sfc_geis` AS `id_exp_sfc_geis`,`g`.`geis_f_initial__Hz` AS `geis_f_initial__Hz`,`g`.`geis_f_final__Hz` AS `geis_f_final__Hz`,`g`.`geis_I_dc__A` AS `geis_I_dc__A`,`g`.`geis_I_amplitude__A` AS `geis_I_amplitude__A`,`g`.`geis_R_initialguess__ohm` AS `geis_R_initialguess__ohm`,`g`.`geis_points_per_decade` AS `geis_points_per_decade` from (((`exp_ec_polcurve` left join (select `data_ec_polcurve`.`id_exp_ec_polcurve` AS `id_exp_ec_polcurve`,min(`data_ec_polcurve`.`id_exp_sfc_ghold`) AS `id_exp_sfc_ghold_first`,min(`data_ec_polcurve`.`id_exp_sfc_geis`) AS `id_exp_sfc_geis_first` from `data_ec_polcurve` group by `data_ec_polcurve`.`id_exp_ec_polcurve`) `a` on((`exp_ec_polcurve`.`id_exp_ec_polcurve` = `a`.`id_exp_ec_polcurve`))) left join (select `exp_ec_expanded`.`id_exp_sfc` AS `id_exp_sfc`,`exp_ec_expanded`.`name_user` AS `name_user`,`exp_ec_expanded`.`name_setup_sfc` AS `name_setup_sfc`,`exp_ec_expanded`.`name_setup_sfc_alias` AS `name_setup_sfc_alias`,`exp_ec_expanded`.`name_setup_sfc_feature` AS `name_setup_sfc_feature`,`exp_ec_expanded`.`name_setup_sfc_type` AS `name_setup_sfc_type`,`exp_ec_expanded`.`t_start__timestamp` AS `t_start__timestamp`,`exp_ec_expanded`.`rawdata_path` AS `rawdata_path`,`exp_ec_expanded`.`rawdata_computer` AS `rawdata_computer`,`exp_ec_expanded`.`id_ML` AS `id_ML`,`exp_ec_expanded`.`id_ML_technique` AS `id_ML_technique`,`exp_ec_expanded`.`id_sample` AS `id_sample`,`exp_ec_expanded`.`id_spot` AS `id_spot`,`exp_ec_expanded`.`force__N` AS `force__N`,`exp_ec_expanded`.`T_stage__degC` AS `T_stage__degC`,`exp_ec_expanded`.`interrupted` AS `interrupted`,`exp_ec_expanded`.`labview_sfc_version` AS `labview_sfc_version`,`exp_ec_expanded`.`db_version` AS `db_version`,`exp_ec_expanded`.`comment` AS `comment`,`exp_ec_expanded`.`t_end__timestamp` AS `t_end__timestamp`,`exp_ec_expanded`.`ec_name_technique` AS `ec_name_technique`,`exp_ec_expanded`.`ec_R_u__ohm` AS `ec_R_u__ohm`,`exp_ec_expanded`.`ec_iR_corr_in_situ__percent` AS `ec_iR_corr_in_situ__percent`,`exp_ec_expanded`.`ec_R_u_determining_exp_ec` AS `ec_R_u_determining_exp_ec`,`exp_ec_expanded`.`ec_E_RE__VvsRHE` AS `ec_E_RE__VvsRHE`,`exp_ec_expanded`.`ec_name_RE` AS `ec_name_RE`,`exp_ec_expanded`.`ec_name_RE_material` AS `ec_name_RE_material`,`exp_ec_expanded`.`ec_name_RE_manufacturer` AS `ec_name_RE_manufacturer`,`exp_ec_expanded`.`ec_name_RE_model` AS `ec_name_RE_model`,`exp_ec_expanded`.`ec_name_CE` AS `ec_name_CE`,`exp_ec_expanded`.`ec_name_CE_material` AS `ec_name_CE_material`,`exp_ec_expanded`.`ec_name_CE_manufacturer` AS `ec_name_CE_manufacturer`,`exp_ec_expanded`.`ec_name_CE_model` AS `ec_name_CE_model`,`exp_ec_expanded`.`ec_name_device` AS `ec_name_device`,`exp_ec_expanded`.`ec_id_control_mode` AS `ec_id_control_mode`,`exp_ec_expanded`.`ec_id_ie_range` AS `ec_id_ie_range`,`exp_ec_expanded`.`ec_id_vch_range` AS `ec_id_vch_range`,`exp_ec_expanded`.`ec_id_ich_range` AS `ec_id_ich_range`,`exp_ec_expanded`.`ec_id_vch_filter` AS `ec_id_vch_filter`,`exp_ec_expanded`.`ec_id_ich_filter` AS `ec_id_ich_filter`,`exp_ec_expanded`.`ec_id_ca_speed` AS `ec_id_ca_speed`,`exp_ec_expanded`.`ec_id_ie_stability` AS `ec_id_ie_stability`,`exp_ec_expanded`.`ec_id_sampling_mode` AS `ec_id_sampling_mode`,`exp_ec_expanded`.`ec_ie_range_auto` AS `ec_ie_range_auto`,`exp_ec_expanded`.`ec_vch_range_auto` AS `ec_vch_range_auto`,`exp_ec_expanded`.`ec_ich_range_auto` AS `ec_ich_range_auto`,`exp_ec_expanded`.`samples_id_sample` AS `samples_id_sample`,`exp_ec_expanded`.`samples_name_sample` AS `samples_name_sample`,`exp_ec_expanded`.`samples_name_user` AS `samples_name_user`,`exp_ec_expanded`.`samples_t_manufactured__timestamp` AS `samples_t_manufactured__timestamp`,`exp_ec_expanded`.`samples_comment` AS `samples_comment`,`exp_ec_expanded`.`samples_total_loading__mg_cm2` AS `samples_total_loading__mg_cm2`,`exp_ec_expanded`.`spots_id_spot` AS `spots_id_spot`,`exp_ec_expanded`.`spots_spot_size__mm2` AS `spots_spot_size__mm2`,`exp_ec_expanded`.`spots_pos_x__mm` AS `spots_pos_x__mm`,`exp_ec_expanded`.`spots_pos_y__mm` AS `spots_pos_y__mm`,`exp_ec_expanded`.`spots_comment` AS `spots_comment`,`exp_ec_expanded`.`spots_total_loading__mg_cm2` AS `spots_total_loading__mg_cm2`,`exp_ec_expanded`.`cv_E_initial__VvsRE` AS `cv_E_initial__VvsRE`,`exp_ec_expanded`.`cv_E_apex1__VvsRE` AS `cv_E_apex1__VvsRE`,`exp_ec_expanded`.`cv_E_apex2__VvsRE` AS `cv_E_apex2__VvsRE`,`exp_ec_expanded`.`cv_E_final__VvsRE` AS `cv_E_final__VvsRE`,`exp_ec_expanded`.`cv_scanrate__mV_s` AS `cv_scanrate__mV_s`,`exp_ec_expanded`.`cv_stepsize__mV` AS `cv_stepsize__mV`,`exp_ec_expanded`.`cv_cycles` AS `cv_cycles`,`exp_ec_expanded`.`ghold_I_hold__A` AS `ghold_I_hold__A`,`exp_ec_expanded`.`ghold_t_hold__s` AS `ghold_t_hold__s`,`exp_ec_expanded`.`ghold_t_samplerate__s` AS `ghold_t_samplerate__s`,`exp_ec_expanded`.`peis_f_initial__Hz` AS `peis_f_initial__Hz`,`exp_ec_expanded`.`peis_f_final__Hz` AS `peis_f_final__Hz`,`exp_ec_expanded`.`peis_E_dc__VvsRE` AS `peis_E_dc__VvsRE`,`exp_ec_expanded`.`peis_E_amplitude__VvsRE` AS `peis_E_amplitude__VvsRE`,`exp_ec_expanded`.`peis_R_initialguess__ohm` AS `peis_R_initialguess__ohm`,`exp_ec_expanded`.`peis_points_per_decade` AS `peis_points_per_decade`,`exp_ec_expanded`.`phold_E_hold__VvsRE` AS `phold_E_hold__VvsRE`,`exp_ec_expanded`.`phold_t_hold__s` AS `phold_t_hold__s`,`exp_ec_expanded`.`phold_t_samplerate__s` AS `phold_t_samplerate__s`,`exp_ec_expanded`.`ppulse_E_hold1__VvsRE` AS `ppulse_E_hold1__VvsRE`,`exp_ec_expanded`.`ppulse_E_hold2__VvsRE` AS `ppulse_E_hold2__VvsRE`,`exp_ec_expanded`.`ppulse_t_hold1__s` AS `ppulse_t_hold1__s`,`exp_ec_expanded`.`ppulse_t_hold2__s` AS `ppulse_t_hold2__s`,`exp_ec_expanded`.`ppulse_t_samplerate__s` AS `ppulse_t_samplerate__s`,`exp_ec_expanded`.`ppulse_cycles` AS `ppulse_cycles`,`exp_ec_expanded`.`gpulse_I_hold1__A` AS `gpulse_I_hold1__A`,`exp_ec_expanded`.`gpulse_I_hold2__A` AS `gpulse_I_hold2__A`,`exp_ec_expanded`.`gpulse_t_hold1__s` AS `gpulse_t_hold1__s`,`exp_ec_expanded`.`gpulse_t_hold2__s` AS `gpulse_t_hold2__s`,`exp_ec_expanded`.`gpulse_t_samplerate__s` AS `gpulse_t_samplerate__s`,`exp_ec_expanded`.`gpulse_cycles` AS `gpulse_cycles`,`exp_ec_expanded`.`ramp_E_initial__VvsRE` AS `ramp_E_initial__VvsRE`,`exp_ec_expanded`.`ramp_E_final__VvsRE` AS `ramp_E_final__VvsRE`,`exp_ec_expanded`.`ramp_scanrate__mV_s` AS `ramp_scanrate__mV_s`,`exp_ec_expanded`.`ramp_stepsize__mV` AS `ramp_stepsize__mV`,`exp_ec_expanded`.`ramp_cycles` AS `ramp_cycles`,`exp_ec_expanded`.`fc_top_name_flow_cell` AS `fc_top_name_flow_cell`,`exp_ec_expanded`.`fc_top_name_flow_cell_name_user` AS `fc_top_name_flow_cell_name_user`,`exp_ec_expanded`.`fc_top_name_flow_cell_material` AS `fc_top_name_flow_cell_material`,`exp_ec_expanded`.`fc_top_name_flow_cell_A_opening_ideal__mm2` AS `fc_top_name_flow_cell_A_opening_ideal__mm2`,`exp_ec_expanded`.`fc_top_name_flow_cell_A_opening_real__mm2` AS `fc_top_name_flow_cell_A_opening_real__mm2`,`exp_ec_expanded`.`fc_top_name_flow_cell_manufacture_date` AS `fc_top_name_flow_cell_manufacture_date`,`exp_ec_expanded`.`fc_top_name_flow_cell_CAD_file` AS `fc_top_name_flow_cell_CAD_file`,`exp_ec_expanded`.`fc_top_name_flow_cell_comment` AS `fc_top_name_flow_cell_comment`,`exp_ec_expanded`.`fc_top_id_sealing` AS `fc_top_id_sealing`,`exp_ec_expanded`.`fc_top_id_sealing_name_user` AS `fc_top_id_sealing_name_user`,`exp_ec_expanded`.`fc_top_id_sealing_material` AS `fc_top_id_sealing_material`,`exp_ec_expanded`.`fc_top_id_sealing_A_sealing__mm2` AS `fc_top_id_sealing_A_sealing__mm2`,`exp_ec_expanded`.`fc_top_id_sealing_A_opening__mm2` AS `fc_top_id_sealing_A_opening__mm2`,`exp_ec_expanded`.`fc_top_id_sealing_thickness__mm` AS `fc_top_id_sealing_thickness__mm`,`exp_ec_expanded`.`fc_top_id_sealing_shaping_method` AS `fc_top_id_sealing_shaping_method`,`exp_ec_expanded`.`fc_top_id_sealing_comment` AS `fc_top_id_sealing_comment`,`exp_ec_expanded`.`fc_top_id_PTL` AS `fc_top_id_PTL`,`exp_ec_expanded`.`fc_top_id_PTL_name_user` AS `fc_top_id_PTL_name_user`,`exp_ec_expanded`.`fc_top_id_PTL_material` AS `fc_top_id_PTL_material`,`exp_ec_expanded`.`fc_top_id_PTL_thickness__mm` AS `fc_top_id_PTL_thickness__mm`,`exp_ec_expanded`.`fc_top_id_PTL_manufacturer` AS `fc_top_id_PTL_manufacturer`,`exp_ec_expanded`.`fc_top_id_PTL_A_PTL__mm2` AS `fc_top_id_PTL_A_PTL__mm2`,`exp_ec_expanded`.`fc_top_id_PTL_shaping_method` AS `fc_top_id_PTL_shaping_method`,`exp_ec_expanded`.`fc_top_id_PTL_comment` AS `fc_top_id_PTL_comment`,`exp_ec_expanded`.`fc_bottom_name_flow_cell` AS `fc_bottom_name_flow_cell`,`exp_ec_expanded`.`fc_bottom_name_flow_cell_name_user` AS `fc_bottom_name_flow_cell_name_user`,`exp_ec_expanded`.`fc_bottom_name_flow_cell_material` AS `fc_bottom_name_flow_cell_material`,`exp_ec_expanded`.`fc_bottom_name_flow_cell_A_opening_ideal__mm2` AS `fc_bottom_name_flow_cell_A_opening_ideal__mm2`,`exp_ec_expanded`.`fc_bottom_name_flow_cell_A_opening_real__mm2` AS `fc_bottom_name_flow_cell_A_opening_real__mm2`,`exp_ec_expanded`.`fc_bottom_name_flow_cell_manufacture_date` AS `fc_bottom_name_flow_cell_manufacture_date`,`exp_ec_expanded`.`fc_bottom_name_flow_cell_CAD_file` AS `fc_bottom_name_flow_cell_CAD_file`,`exp_ec_expanded`.`fc_bottom_name_flow_cell_comment` AS `fc_bottom_name_flow_cell_comment`,`exp_ec_expanded`.`fc_bottom_id_sealing` AS `fc_bottom_id_sealing`,`exp_ec_expanded`.`fc_bottom_id_sealing_name_user` AS `fc_bottom_id_sealing_name_user`,`exp_ec_expanded`.`fc_bottom_id_sealing_material` AS `fc_bottom_id_sealing_material`,`exp_ec_expanded`.`fc_bottom_id_sealing_A_sealing__mm2` AS `fc_bottom_id_sealing_A_sealing__mm2`,`exp_ec_expanded`.`fc_bottom_id_sealing_A_opening__mm2` AS `fc_bottom_id_sealing_A_opening__mm2`,`exp_ec_expanded`.`fc_bottom_id_sealing_thickness__mm` AS `fc_bottom_id_sealing_thickness__mm`,`exp_ec_expanded`.`fc_bottom_id_sealing_shaping_method` AS `fc_bottom_id_sealing_shaping_method`,`exp_ec_expanded`.`fc_bottom_id_sealing_comment` AS `fc_bottom_id_sealing_comment`,`exp_ec_expanded`.`fc_bottom_id_PTL` AS `fc_bottom_id_PTL`,`exp_ec_expanded`.`fc_bottom_id_PTL_name_user` AS `fc_bottom_id_PTL_name_user`,`exp_ec_expanded`.`fc_bottom_id_PTL_material` AS `fc_bottom_id_PTL_material`,`exp_ec_expanded`.`fc_bottom_id_PTL_thickness__mm` AS `fc_bottom_id_PTL_thickness__mm`,`exp_ec_expanded`.`fc_bottom_id_PTL_manufacturer` AS `fc_bottom_id_PTL_manufacturer`,`exp_ec_expanded`.`fc_bottom_id_PTL_A_PTL__mm2` AS `fc_bottom_id_PTL_A_PTL__mm2`,`exp_ec_expanded`.`fc_bottom_id_PTL_shaping_method` AS `fc_bottom_id_PTL_shaping_method`,`exp_ec_expanded`.`fc_bottom_id_PTL_comment` AS `fc_bottom_id_PTL_comment`,`exp_ec_expanded`.`fe_top_id_pump_in` AS `fe_top_id_pump_in`,`exp_ec_expanded`.`fe_top_id_pump_in_manufacturer` AS `fe_top_id_pump_in_manufacturer`,`exp_ec_expanded`.`fe_top_id_pump_in_model` AS `fe_top_id_pump_in_model`,`exp_ec_expanded`.`fe_top_id_pump_in_device` AS `fe_top_id_pump_in_device`,`exp_ec_expanded`.`fe_top_id_tubing_in` AS `fe_top_id_tubing_in`,`exp_ec_expanded`.`fe_top_id_tubing_in_name_tubing` AS `fe_top_id_tubing_in_name_tubing`,`exp_ec_expanded`.`fe_top_id_tubing_in_inner_diameter__mm` AS `fe_top_id_tubing_in_inner_diameter__mm`,`exp_ec_expanded`.`fe_top_id_tubing_in_color_code` AS `fe_top_id_tubing_in_color_code`,`exp_ec_expanded`.`fe_top_id_tubing_in_manufacturer` AS `fe_top_id_tubing_in_manufacturer`,`exp_ec_expanded`.`fe_top_id_tubing_in_model` AS `fe_top_id_tubing_in_model`,`exp_ec_expanded`.`fe_top_pump_rate_in__rpm` AS `fe_top_pump_rate_in__rpm`,`exp_ec_expanded`.`fe_top_id_pump_out` AS `fe_top_id_pump_out`,`exp_ec_expanded`.`fe_top_id_pump_out_manufacturer` AS `fe_top_id_pump_out_manufacturer`,`exp_ec_expanded`.`fe_top_id_pump_out_model` AS `fe_top_id_pump_out_model`,`exp_ec_expanded`.`fe_top_id_pump_out_device` AS `fe_top_id_pump_out_device`,`exp_ec_expanded`.`fe_top_id_tubing_out` AS `fe_top_id_tubing_out`,`exp_ec_expanded`.`fe_top_id_tubing_out_name_tubing` AS `fe_top_id_tubing_out_name_tubing`,`exp_ec_expanded`.`fe_top_id_tubing_out_inner_diameter__mm` AS `fe_top_id_tubing_out_inner_diameter__mm`,`exp_ec_expanded`.`fe_top_id_tubing_out_color_code` AS `fe_top_id_tubing_out_color_code`,`exp_ec_expanded`.`fe_top_id_tubing_out_manufacturer` AS `fe_top_id_tubing_out_manufacturer`,`exp_ec_expanded`.`fe_top_id_tubing_out_model` AS `fe_top_id_tubing_out_model`,`exp_ec_expanded`.`fe_top_pump_rate_out__rpm` AS `fe_top_pump_rate_out__rpm`,`exp_ec_expanded`.`fe_top_flow_rate_real__mul_min` AS `fe_top_flow_rate_real__mul_min`,`exp_ec_expanded`.`fe_top_name_electrolyte` AS `fe_top_name_electrolyte`,`exp_ec_expanded`.`fe_top_c_electrolyte__mol_L` AS `fe_top_c_electrolyte__mol_L`,`exp_ec_expanded`.`fe_top_T_electrolyte__degC` AS `fe_top_T_electrolyte__degC`,`exp_ec_expanded`.`fe_bottom_id_pump_in` AS `fe_bottom_id_pump_in`,`exp_ec_expanded`.`fe_bottom_id_pump_in_manufacturer` AS `fe_bottom_id_pump_in_manufacturer`,`exp_ec_expanded`.`fe_bottom_id_pump_in_model` AS `fe_bottom_id_pump_in_model`,`exp_ec_expanded`.`fe_bottom_id_pump_in_device` AS `fe_bottom_id_pump_in_device`,`exp_ec_expanded`.`fe_bottom_id_tubing_in` AS `fe_bottom_id_tubing_in`,`exp_ec_expanded`.`fe_bottom_id_tubing_in_name_tubing` AS `fe_bottom_id_tubing_in_name_tubing`,`exp_ec_expanded`.`fe_bottom_id_tubing_in_inner_diameter__mm` AS `fe_bottom_id_tubing_in_inner_diameter__mm`,`exp_ec_expanded`.`fe_bottom_id_tubing_in_color_code` AS `fe_bottom_id_tubing_in_color_code`,`exp_ec_expanded`.`fe_bottom_id_tubing_in_manufacturer` AS `fe_bottom_id_tubing_in_manufacturer`,`exp_ec_expanded`.`fe_bottom_id_tubing_in_model` AS `fe_bottom_id_tubing_in_model`,`exp_ec_expanded`.`fe_bottom_pump_rate_in__rpm` AS `fe_bottom_pump_rate_in__rpm`,`exp_ec_expanded`.`fe_bottom_id_pump_out` AS `fe_bottom_id_pump_out`,`exp_ec_expanded`.`fe_bottom_id_pump_out_manufacturer` AS `fe_bottom_id_pump_out_manufacturer`,`exp_ec_expanded`.`fe_bottom_id_pump_out_model` AS `fe_bottom_id_pump_out_model`,`exp_ec_expanded`.`fe_bottom_id_pump_out_device` AS `fe_bottom_id_pump_out_device`,`exp_ec_expanded`.`fe_bottom_id_tubing_out` AS `fe_bottom_id_tubing_out`,`exp_ec_expanded`.`fe_bottom_id_tubing_out_name_tubing` AS `fe_bottom_id_tubing_out_name_tubing`,`exp_ec_expanded`.`fe_bottom_id_tubing_out_inner_diameter__mm` AS `fe_bottom_id_tubing_out_inner_diameter__mm`,`exp_ec_expanded`.`fe_bottom_id_tubing_out_color_code` AS `fe_bottom_id_tubing_out_color_code`,`exp_ec_expanded`.`fe_bottom_id_tubing_out_manufacturer` AS `fe_bottom_id_tubing_out_manufacturer`,`exp_ec_expanded`.`fe_bottom_id_tubing_out_model` AS `fe_bottom_id_tubing_out_model`,`exp_ec_expanded`.`fe_bottom_pump_rate_out__rpm` AS `fe_bottom_pump_rate_out__rpm`,`exp_ec_expanded`.`fe_bottom_flow_rate_real__mul_min` AS `fe_bottom_flow_rate_real__mul_min`,`exp_ec_expanded`.`fe_bottom_name_electrolyte` AS `fe_bottom_name_electrolyte`,`exp_ec_expanded`.`fe_bottom_c_electrolyte__mol_L` AS `fe_bottom_c_electrolyte__mol_L`,`exp_ec_expanded`.`fe_bottom_T_electrolyte__degC` AS `fe_bottom_T_electrolyte__degC`,`exp_ec_expanded`.`fg_top_Arring_name_gas` AS `fg_top_Arring_name_gas`,`exp_ec_expanded`.`fg_top_Arring_flow_rate__mL_min` AS `fg_top_Arring_flow_rate__mL_min`,`exp_ec_expanded`.`fg_top_purgevial_name_gas` AS `fg_top_purgevial_name_gas`,`exp_ec_expanded`.`fg_top_purgevial_flow_rate__mL_min` AS `fg_top_purgevial_flow_rate__mL_min`,`exp_ec_expanded`.`fg_top_main_name_gas` AS `fg_top_main_name_gas`,`exp_ec_expanded`.`fg_top_main_flow_rate__mL_min` AS `fg_top_main_flow_rate__mL_min`,`exp_ec_expanded`.`fg_bottom_Arring_name_gas` AS `fg_bottom_Arring_name_gas`,`exp_ec_expanded`.`fg_bottom_Arring_flow_rate__mL_min` AS `fg_bottom_Arring_flow_rate__mL_min`,`exp_ec_expanded`.`fg_bottom_purgevial_name_gas` AS `fg_bottom_purgevial_name_gas`,`exp_ec_expanded`.`fg_bottom_purgevial_flow_rate__mL_min` AS `fg_bottom_purgevial_flow_rate__mL_min`,`exp_ec_expanded`.`fg_bottom_main_name_gas` AS `fg_bottom_main_name_gas`,`exp_ec_expanded`.`fg_bottom_main_flow_rate__mL_min` AS `fg_bottom_main_flow_rate__mL_min` from `exp_ec_expanded`) `e` on((`a`.`id_exp_sfc_ghold_first` = `e`.`id_exp_sfc`))) left join (select `exp_ec_geis`.`id_exp_sfc` AS `id_exp_sfc_geis`,`exp_ec_geis`.`f_initial__Hz` AS `geis_f_initial__Hz`,`exp_ec_geis`.`f_final__Hz` AS `geis_f_final__Hz`,`exp_ec_geis`.`I_dc__A` AS `geis_I_dc__A`,`exp_ec_geis`.`I_amplitude__A` AS `geis_I_amplitude__A`,`exp_ec_geis`.`R_initialguess__ohm` AS `geis_R_initialguess__ohm`,`exp_ec_geis`.`points_per_decade` AS `geis_points_per_decade` from `exp_ec_geis`) `g` on((`a`.`id_exp_sfc_geis_first` = `g`.`id_exp_sfc_geis`))) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `exp_icpms_batch_expanded`
--

/*!50001 DROP VIEW IF EXISTS `exp_icpms_batch_expanded`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `exp_icpms_batch_expanded` AS select `a`.`id_exp_icpms` AS `id_exp_icpms`,`a`.`name_isotope_analyte` AS `name_isotope_analyte`,`a`.`name_isotope_internalstandard` AS `name_isotope_internalstandard`,`a`.`name_sample` AS `name_sample`,`a`.`name_user` AS `name_user`,`a`.`name_setup_icpms` AS `name_setup_icpms`,`a`.`t_start__timestamp_icpms_pc` AS `t_start__timestamp_icpms_pc`,`a`.`t_duration__s` AS `t_duration__s`,`a`.`t_duration_planned__s` AS `t_duration_planned__s`,`a`.`type_experiment` AS `type_experiment`,`a`.`plasma_mode` AS `plasma_mode`,`a`.`tune_mode` AS `tune_mode`,`a`.`num_of_scans` AS `num_of_scans`,`a`.`id_exp_icpms_calibration_set` AS `id_exp_icpms_calibration_set`,`a`.`gas_dilution_factor` AS `gas_dilution_factor`,`a`.`name_gas_collision` AS `name_gas_collision`,`a`.`flow_rate_collision__mL_min` AS `flow_rate_collision__mL_min`,`a`.`name_gas_reaction` AS `name_gas_reaction`,`a`.`flow_rate_reaction__mL_min` AS `flow_rate_reaction__mL_min`,`a`.`comment` AS `comment`,`a`.`name_computer_inserted_data` AS `name_computer_inserted_data`,`a`.`file_path_rawdata` AS `file_path_rawdata`,`a`.`t_inserted_data__timestamp` AS `t_inserted_data__timestamp`,`a`.`file_name_rawdata` AS `file_name_rawdata`,`a`.`batch_name` AS `batch_name`,`exp_icpms_analyte_internalstandard`.`c_analyte__mug_L` AS `c_analyte_0__mug_L`,`exp_icpms_analyte_internalstandard`.`c_internalstandard__mug_L` AS `c_internalstandard__mug_L`,`exp_icpms_analyte_internalstandard`.`t_integration_analyte__s` AS `t_integration_analyte__s`,`exp_icpms_analyte_internalstandard`.`t_integration_internalstandard__s` AS `t_integration_internalstandard__s`,`exp_icpms_calibration_params`.`calibration_slope__countratio_mug_L` AS `calibration_slope__countratio_mug_L`,`exp_icpms_calibration_params`.`delta_calibration_slope__countratio_mug_L` AS `delta_calibration_slope__countratio_mug_L`,`exp_icpms_calibration_params`.`calibration_intercept__countratio` AS `calibration_intercept__countratio`,`exp_icpms_calibration_params`.`delta_calibration_intercept__countratio` AS `delta_calibration_intercept__countratio`,`exp_icpms_calibration_params`.`Rsquared` AS `Rsquared`,`exp_icpms_calibration_params`.`calibration_method` AS `calibration_method`,`exp_icpms_calibration_params`.`file_path_calibration_plot` AS `file_path_calibration_plot`,`exp_icpms_calibration_params`.`name_computer_inserted_data` AS `name_computer_inserted_calibration_data`,`exp_icpms_calibration_params`.`t_inserted_data__timestamp` AS `t_inserted_calibration_data__timestamp`,`a`.`counts_analyte_mean` AS `counts_analyte_mean`,`a`.`counts_analyte_std` AS `counts_analyte_std`,`a`.`counts_internalstandard_mean` AS `counts_internalstandard_mean`,`a`.`counts_internalstandard_std` AS `counts_internalstandard_std`,(`a`.`counts_analyte_mean` / `a`.`counts_internalstandard_mean`) AS `a_is__countratio`,(((`a`.`counts_analyte_mean` / `a`.`counts_internalstandard_mean`) - `exp_icpms_calibration_params`.`calibration_intercept__countratio`) / `exp_icpms_calibration_params`.`calibration_slope__countratio_mug_L`) AS `c_a__mug_L` from (((select `exp_icpms`.`id_exp_icpms` AS `id_exp_icpms`,`exp_icpms`.`name_sample` AS `name_sample`,`exp_icpms`.`name_user` AS `name_user`,`exp_icpms`.`name_setup_icpms` AS `name_setup_icpms`,`exp_icpms`.`t_start__timestamp_icpms_pc` AS `t_start__timestamp_icpms_pc`,`exp_icpms`.`t_duration__s` AS `t_duration__s`,`exp_icpms`.`t_duration_planned__s` AS `t_duration_planned__s`,`exp_icpms`.`type_experiment` AS `type_experiment`,`exp_icpms`.`plasma_mode` AS `plasma_mode`,`exp_icpms`.`tune_mode` AS `tune_mode`,`exp_icpms`.`num_of_scans` AS `num_of_scans`,`exp_icpms`.`id_exp_icpms_calibration_set` AS `id_exp_icpms_calibration_set`,`exp_icpms`.`gas_dilution_factor` AS `gas_dilution_factor`,`exp_icpms`.`name_gas_collision` AS `name_gas_collision`,`exp_icpms`.`flow_rate_collision__mL_min` AS `flow_rate_collision__mL_min`,`exp_icpms`.`name_gas_reaction` AS `name_gas_reaction`,`exp_icpms`.`flow_rate_reaction__mL_min` AS `flow_rate_reaction__mL_min`,`exp_icpms`.`comment` AS `comment`,`exp_icpms`.`name_computer_inserted_data` AS `name_computer_inserted_data`,`exp_icpms`.`file_path_rawdata` AS `file_path_rawdata`,`exp_icpms`.`t_inserted_data__timestamp` AS `t_inserted_data__timestamp`,`exp_icpms`.`file_name_rawdata` AS `file_name_rawdata`,`exp_icpms`.`batch_name` AS `batch_name`,`data_icpms`.`name_isotope_analyte` AS `name_isotope_analyte`,`data_icpms`.`name_isotope_internalstandard` AS `name_isotope_internalstandard`,avg(`data_icpms`.`counts_analyte`) AS `counts_analyte_mean`,std(`data_icpms`.`counts_analyte`) AS `counts_analyte_std`,avg(`data_icpms`.`counts_internalstandard`) AS `counts_internalstandard_mean`,std(`data_icpms`.`counts_internalstandard`) AS `counts_internalstandard_std` from (`data_icpms` left join `exp_icpms` on((`data_icpms`.`id_exp_icpms` = `exp_icpms`.`id_exp_icpms`))) where `exp_icpms`.`id_exp_icpms_calibration_set` in (select distinct `exp_icpms`.`id_exp_icpms_calibration_set` from `exp_icpms` where (`exp_icpms`.`type_experiment` = 'batch')) group by `exp_icpms`.`id_exp_icpms`,`data_icpms`.`name_isotope_analyte`,`data_icpms`.`name_isotope_internalstandard`) `a` left join `exp_icpms_calibration_params` on(((`a`.`id_exp_icpms_calibration_set` = `exp_icpms_calibration_params`.`id_exp_icpms_calibration_set`) and (`a`.`name_isotope_analyte` = `exp_icpms_calibration_params`.`name_isotope_analyte`) and (`a`.`name_isotope_internalstandard` = `exp_icpms_calibration_params`.`name_isotope_internalstandard`)))) left join `exp_icpms_analyte_internalstandard` on(((`a`.`id_exp_icpms` = `exp_icpms_analyte_internalstandard`.`id_exp_icpms`) and (`a`.`name_isotope_analyte` = `exp_icpms_analyte_internalstandard`.`name_isotope_analyte`) and (`a`.`name_isotope_internalstandard` = `exp_icpms_analyte_internalstandard`.`name_isotope_internalstandard`)))) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `exp_icpms_integration_expanded`
--

/*!50001 DROP VIEW IF EXISTS `exp_icpms_integration_expanded`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `exp_icpms_integration_expanded` AS select `isotopes`.`element` AS `element`,`icp_int`.`id_exp_icpms` AS `id_exp_icpms`,`icp_int`.`name_isotope_analyte` AS `name_isotope_analyte`,`icp_int`.`name_isotope_internalstandard` AS `name_isotope_internalstandard`,`icp_int`.`id_ana_integration_icpms` AS `id_ana_integration_icpms`,`icp_int`.`name_analysis` AS `name_analysis`,`icp_int`.`id_exp_ec_dataset` AS `id_exp_ec_dataset`,`ana`.`id_data_integration_icpms_baseline` AS `id_data_integration_icpms_baseline`,`ana`.`id_data_integration_icpms_begin` AS `id_data_integration_icpms_begin`,`ana`.`id_data_integration_icpms_end` AS `id_data_integration_icpms_end`,`ana`.`t_integration_icpms_baseline__timestamp` AS `t_integration_icpms_baseline__timestamp`,`ana`.`t_integration_icpms_begin__timestamp` AS `t_integration_icpms_begin__timestamp`,`ana`.`t_integration_icpms_end__timestamp` AS `t_integration_icpms_end__timestamp`,`ana`.`m_dissolved_simps__ng` AS `m_dissolved_simps__ng`,`ana`.`m_dissolved_trapz__ng` AS `m_dissolved_trapz__ng`,`ana`.`dm_dt_offset__ng_s` AS `dm_dt_offset__ng_s`,`ana`.`no_of_datapoints_av_icpms` AS `no_of_datapoints_av_icpms`,`ana`.`no_of_datapoints_rolling_icpms` AS `no_of_datapoints_rolling_icpms`,`ana`.`auto_integration_icpms` AS `auto_integration_icpms`,`exp_ec_datasets`.`name_exp_ec_dataset` AS `name_exp_ec_dataset`,`expanded`.`name_sample` AS `name_sample`,`expanded`.`name_user` AS `name_user`,`expanded`.`name_setup_icpms` AS `name_setup_icpms`,`expanded`.`t_start__timestamp_icpms_pc` AS `t_start__timestamp_icpms_pc`,`expanded`.`t_duration__s` AS `t_duration__s`,`expanded`.`t_duration_planned__s` AS `t_duration_planned__s`,`expanded`.`type_experiment` AS `type_experiment`,`expanded`.`plasma_mode` AS `plasma_mode`,`expanded`.`tune_mode` AS `tune_mode`,`expanded`.`num_of_scans` AS `num_of_scans`,`expanded`.`id_exp_icpms_calibration_set` AS `id_exp_icpms_calibration_set`,`expanded`.`gas_dilution_factor` AS `gas_dilution_factor`,`expanded`.`name_gas_collision` AS `name_gas_collision`,`expanded`.`flow_rate_collision__mL_min` AS `flow_rate_collision__mL_min`,`expanded`.`name_gas_reaction` AS `name_gas_reaction`,`expanded`.`flow_rate_reaction__mL_min` AS `flow_rate_reaction__mL_min`,`expanded`.`comment` AS `comment`,`expanded`.`name_computer_inserted_data` AS `name_computer_inserted_data`,`expanded`.`file_path_rawdata` AS `file_path_rawdata`,`expanded`.`batch_name` AS `batch_name`,`expanded`.`t_inserted_data__timestamp` AS `t_inserted_data__timestamp`,`expanded`.`file_name_rawdata` AS `file_name_rawdata`,`expanded`.`t_start_delaycorrected__timestamp_sfc_pc` AS `t_start_delaycorrected__timestamp_sfc_pc`,`expanded`.`t_end_delaycorrected__timestamp_sfc_pc` AS `t_end_delaycorrected__timestamp_sfc_pc`,`expanded`.`name_setup_sfc` AS `name_setup_sfc`,`expanded`.`t_start__timestamp_sfc_pc` AS `t_start__timestamp_sfc_pc`,`expanded`.`t_delay__s` AS `t_delay__s`,`expanded`.`flow_rate_real__mul_min` AS `flow_rate_real__mul_min`,`expanded`.`calibration_slope__countratio_mug_L` AS `calibration_slope__countratio_mug_L`,`expanded`.`delta_calibration_slope__countratio_mug_L` AS `delta_calibration_slope__countratio_mug_L`,`expanded`.`calibration_intercept__countratio` AS `calibration_intercept__countratio`,`expanded`.`delta_calibration_intercept__countratio` AS `delta_calibration_intercept__countratio`,`expanded`.`Rsquared` AS `Rsquared`,`expanded`.`calibration_method` AS `calibration_method`,`expanded`.`file_path_calibration_plot` AS `file_path_calibration_plot`,`expanded`.`name_computer_inserted_calibration_data` AS `name_computer_inserted_calibration_data`,`expanded`.`t_inserted_calibration_data__timestamp` AS `t_inserted_calibration_data__timestamp`,`isotopes`.`name_isotope` AS `name_isotope`,`e`.`M__g_mol` AS `M__g_mol`,((`ana`.`m_dissolved_simps__ng` / `e`.`M__g_mol`) * pow(10,-(9))) AS `n_dissolved_simps__mol`,((`ana`.`m_dissolved_trapz__ng` / `e`.`M__g_mol`) * pow(10,-(9))) AS `n_dissolved_trapz__mol` from ((((((select `exp_icpms_integration`.`id_exp_icpms` AS `id_exp_icpms`,`exp_icpms_integration`.`name_isotope_analyte` AS `name_isotope_analyte`,`exp_icpms_integration`.`name_isotope_internalstandard` AS `name_isotope_internalstandard`,`exp_icpms_integration`.`name_analysis` AS `name_analysis`,`exp_icpms_integration`.`id_exp_ec_dataset` AS `id_exp_ec_dataset`,`exp_icpms_integration`.`id_ana_integration` AS `id_ana_integration_icpms` from `exp_icpms_integration`) `icp_int` left join (select `ana_integrations`.`id_ana_integration` AS `id_ana_integration_icpms`,`ana_integrations`.`id_data_integration_baseline` AS `id_data_integration_icpms_baseline`,`ana_integrations`.`id_data_integration_begin` AS `id_data_integration_icpms_begin`,`ana_integrations`.`id_data_integration_end` AS `id_data_integration_icpms_end`,`ana_integrations`.`t_integration_baseline__timestamp` AS `t_integration_icpms_baseline__timestamp`,`ana_integrations`.`t_integration_begin__timestamp` AS `t_integration_icpms_begin__timestamp`,`ana_integrations`.`t_integration_end__timestamp` AS `t_integration_icpms_end__timestamp`,`ana_integrations`.`area_integrated_simps` AS `m_dissolved_simps__ng`,`ana_integrations`.`area_integrated_trapz` AS `m_dissolved_trapz__ng`,`ana_integrations`.`y_offset` AS `dm_dt_offset__ng_s`,`ana_integrations`.`no_of_datapoints_avg` AS `no_of_datapoints_av_icpms`,`ana_integrations`.`no_of_datapoints_rolling` AS `no_of_datapoints_rolling_icpms`,`ana_integrations`.`auto_integration` AS `auto_integration_icpms` from `ana_integrations`) `ana` on((`icp_int`.`id_ana_integration_icpms` = `ana`.`id_ana_integration_icpms`))) left join `exp_ec_datasets` on((`icp_int`.`id_exp_ec_dataset` = `exp_ec_datasets`.`id_exp_ec_dataset`))) left join `exp_icpms_sfc_expanded` `expanded` on(((`icp_int`.`id_exp_icpms` = `expanded`.`id_exp_icpms`) and (`icp_int`.`name_isotope_analyte` = `expanded`.`name_isotope_analyte`) and (`icp_int`.`name_isotope_internalstandard` = `expanded`.`name_isotope_internalstandard`)))) left join `isotopes` on((`icp_int`.`name_isotope_analyte` = `isotopes`.`name_isotope`))) left join `elements` `e` on((`isotopes`.`element` = `e`.`element`))) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `exp_icpms_sfc_batch_expanded`
--

/*!50001 DROP VIEW IF EXISTS `exp_icpms_sfc_batch_expanded`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `exp_icpms_sfc_batch_expanded` AS select `exp_icpms_sfc_batch`.`id_exp_icpms` AS `id_exp_icpms`,`exp_icpms_analyte_internalstandard`.`name_isotope_analyte` AS `name_isotope_analyte`,`exp_icpms_analyte_internalstandard`.`name_isotope_internalstandard` AS `name_isotope_internalstandard`,`exp_icpms_analyte_internalstandard`.`id_exp_icpms_calibration_set` AS `id_exp_icpms_calibration_set`,`exp_icpms_sfc_batch`.`id_exp_icpms_sfc_online` AS `id_exp_icpms_sfc_online`,`exp_icpms_sfc_batch`.`name_analysis` AS `name_analysis`,`exp_icpms_sfc_batch`.`id_exp_ec_dataset` AS `id_exp_ec_dataset`,`exp_ec_datasets`.`name_exp_ec_dataset` AS `name_exp_ec_dataset`,`exp_icpms_sfc_batch`.`name_setup_sfc` AS `name_setup_sfc`,`exp_icpms_sfc_batch`.`location` AS `location`,`exp_icpms_sfc_batch`.`t_delay__s` AS `t_delay__s`,`exp_icpms_sfc_batch`.`t_start__timestamp_sfc_pc` AS `t_start__timestamp_sfc_pc`,`exp_icpms_sfc_batch`.`t_end__timestamp_sfc_pc` AS `t_end__timestamp_sfc_pc`,(`exp_icpms_sfc_batch`.`t_start__timestamp_sfc_pc` - interval `exp_icpms_sfc_batch`.`t_delay__s` second) AS `t_start_delaycorrected__timestamp_sfc_pc`,(`exp_icpms_sfc_batch`.`t_end__timestamp_sfc_pc` - interval `exp_icpms_sfc_batch`.`t_delay__s` second) AS `t_end_delaycorrected__timestamp_sfc_pc`,`exp_icpms_sfc_batch`.`m_start__g` AS `m_start__g`,`exp_icpms_sfc_batch`.`m_end__g` AS `m_end__g`,`exp_icpms_sfc_batch`.`density__g_mL` AS `density__g_mL`,`exp_icpms_sfc_batch`.`comment` AS `comment`,`exp_icpms`.`name_sample` AS `name_sample`,`exp_icpms`.`name_user` AS `name_user`,`exp_icpms`.`name_setup_icpms` AS `name_setup_icpms`,`exp_icpms`.`t_start__timestamp_icpms_pc` AS `t_start__timestamp_icpms_pc`,`exp_icpms`.`t_duration__s` AS `t_duration__s`,`exp_icpms`.`t_duration_planned__s` AS `t_duration_planned__s`,`exp_icpms`.`type_experiment` AS `type_experiment`,`exp_icpms`.`plasma_mode` AS `plasma_mode`,`exp_icpms`.`tune_mode` AS `tune_mode`,`exp_icpms`.`num_of_scans` AS `num_of_scans`,`exp_icpms`.`gas_dilution_factor` AS `gas_dilution_factor`,`exp_icpms`.`name_gas_collision` AS `name_gas_collision`,`exp_icpms`.`flow_rate_collision__mL_min` AS `flow_rate_collision__mL_min`,`exp_icpms`.`name_gas_reaction` AS `name_gas_reaction`,`exp_icpms`.`flow_rate_reaction__mL_min` AS `flow_rate_reaction__mL_min`,`exp_icpms`.`name_computer_inserted_data` AS `name_computer_inserted_data`,`exp_icpms`.`file_path_rawdata` AS `file_path_rawdata`,`exp_icpms`.`t_inserted_data__timestamp` AS `t_inserted_data__timestamp`,`exp_icpms`.`file_name_rawdata` AS `file_name_rawdata`,`exp_icpms`.`batch_name` AS `batch_name`,`exp_icpms_analyte_internalstandard`.`c_analyte__mug_L` AS `c_analyte__mug_L`,`exp_icpms_analyte_internalstandard`.`c_internalstandard__mug_L` AS `c_internalstandard__mug_L`,`exp_icpms_analyte_internalstandard`.`t_integration_analyte__s` AS `t_integration_analyte__s`,`exp_icpms_analyte_internalstandard`.`t_integration_internalstandard__s` AS `t_integration_internalstandard__s`,`a`.`a_is__countratio` AS `a_is__countratio`,`a`.`a_is_std__countratio` AS `a_is_std__countratio`,`exp_icpms_calibration_params`.`calibration_slope__countratio_mug_L` AS `calibration_slope__countratio_mug_L`,`exp_icpms_calibration_params`.`delta_calibration_slope__countratio_mug_L` AS `delta_calibration_slope__countratio_mug_L`,`exp_icpms_calibration_params`.`calibration_intercept__countratio` AS `calibration_intercept__countratio`,`exp_icpms_calibration_params`.`delta_calibration_intercept__countratio` AS `delta_calibration_intercept__countratio`,`exp_icpms_calibration_params`.`Rsquared` AS `Rsquared`,`exp_icpms_calibration_params`.`calibration_method` AS `calibration_method`,`exp_icpms_calibration_params`.`file_path_calibration_plot` AS `file_path_calibration_plot`,`exp_icpms_calibration_params`.`name_computer_inserted_data` AS `name_computer_inserted_calibration_data`,`exp_icpms_calibration_params`.`t_inserted_data__timestamp` AS `t_inserted_calibration_data__timestamp`,timestampdiff(SECOND,`exp_icpms_sfc_batch`.`t_start__timestamp_sfc_pc`,`exp_icpms_sfc_batch`.`t_end__timestamp_sfc_pc`) AS `Delta_t__s`,((((`exp_icpms_sfc_batch`.`m_end__g` - `exp_icpms_sfc_batch`.`m_start__g`) / `exp_icpms_sfc_batch`.`density__g_mL`) * 1000) / (timestampdiff(SECOND,`exp_icpms_sfc_batch`.`t_start__timestamp_sfc_pc`,`exp_icpms_sfc_batch`.`t_end__timestamp_sfc_pc`) / 60)) AS `flow_rate_real__mul_min`,((`a`.`a_is__countratio` - `exp_icpms_calibration_params`.`calibration_intercept__countratio`) / `exp_icpms_calibration_params`.`calibration_slope__countratio_mug_L`) AS `c_a__mug_L`,((((`a`.`a_is__countratio` - `exp_icpms_calibration_params`.`calibration_intercept__countratio`) / `exp_icpms_calibration_params`.`calibration_slope__countratio_mug_L`) * ((((`exp_icpms_sfc_batch`.`m_end__g` - `exp_icpms_sfc_batch`.`m_start__g`) / `exp_icpms_sfc_batch`.`density__g_mL`) * 1000) / (timestampdiff(SECOND,`exp_icpms_sfc_batch`.`t_start__timestamp_sfc_pc`,`exp_icpms_sfc_batch`.`t_end__timestamp_sfc_pc`) / 60))) / (1000 * 60)) AS `dm_dt__ng_s`,(((((`a`.`a_is__countratio` - `exp_icpms_calibration_params`.`calibration_intercept__countratio`) / `exp_icpms_calibration_params`.`calibration_slope__countratio_mug_L`) * ((((`exp_icpms_sfc_batch`.`m_end__g` - `exp_icpms_sfc_batch`.`m_start__g`) / `exp_icpms_sfc_batch`.`density__g_mL`) * 1000) / (timestampdiff(SECOND,`exp_icpms_sfc_batch`.`t_start__timestamp_sfc_pc`,`exp_icpms_sfc_batch`.`t_end__timestamp_sfc_pc`) / 60))) / (1000 * 60)) * timestampdiff(SECOND,`exp_icpms_sfc_batch`.`t_start__timestamp_sfc_pc`,`exp_icpms_sfc_batch`.`t_end__timestamp_sfc_pc`)) AS `m_batch__ng`,(((((((`a`.`a_is__countratio` - `exp_icpms_calibration_params`.`calibration_intercept__countratio`) / `exp_icpms_calibration_params`.`calibration_slope__countratio_mug_L`) * ((((`exp_icpms_sfc_batch`.`m_end__g` - `exp_icpms_sfc_batch`.`m_start__g`) / `exp_icpms_sfc_batch`.`density__g_mL`) * 1000) / (timestampdiff(SECOND,`exp_icpms_sfc_batch`.`t_start__timestamp_sfc_pc`,`exp_icpms_sfc_batch`.`t_end__timestamp_sfc_pc`) / 60))) / (1000 * 60)) * timestampdiff(SECOND,`exp_icpms_sfc_batch`.`t_start__timestamp_sfc_pc`,`exp_icpms_sfc_batch`.`t_end__timestamp_sfc_pc`)) / `e`.`M__g_mol`) * pow(10,-(9))) AS `n_batch__mol` from (((((((`exp_icpms_sfc_batch` left join `exp_icpms_analyte_internalstandard` on((`exp_icpms_sfc_batch`.`id_exp_icpms` = `exp_icpms_analyte_internalstandard`.`id_exp_icpms`))) left join (select `data_icpms`.`id_exp_icpms` AS `id_exp_icpms`,`data_icpms`.`name_isotope_analyte` AS `name_isotope_analyte`,`data_icpms`.`name_isotope_internalstandard` AS `name_isotope_internalstandard`,(avg(`data_icpms`.`counts_analyte`) / avg(`data_icpms`.`counts_internalstandard`)) AS `a_is__countratio`,std((`data_icpms`.`counts_analyte` / `data_icpms`.`counts_internalstandard`)) AS `a_is_std__countratio` from `data_icpms` group by `data_icpms`.`id_exp_icpms`,`data_icpms`.`name_isotope_analyte`,`data_icpms`.`name_isotope_internalstandard`) `a` on(((`exp_icpms_sfc_batch`.`id_exp_icpms` = `a`.`id_exp_icpms`) and (`exp_icpms_analyte_internalstandard`.`name_isotope_analyte` = `a`.`name_isotope_analyte`) and (`exp_icpms_analyte_internalstandard`.`name_isotope_internalstandard` = `a`.`name_isotope_internalstandard`)))) left join `exp_icpms_calibration_params` on(((`exp_icpms_analyte_internalstandard`.`name_isotope_analyte` = `exp_icpms_calibration_params`.`name_isotope_analyte`) and (`exp_icpms_analyte_internalstandard`.`name_isotope_internalstandard` = `exp_icpms_calibration_params`.`name_isotope_internalstandard`) and (`exp_icpms_analyte_internalstandard`.`id_exp_icpms_calibration_set` = `exp_icpms_calibration_params`.`id_exp_icpms_calibration_set`)))) left join `exp_ec_datasets` on((`exp_icpms_sfc_batch`.`id_exp_ec_dataset` = `exp_ec_datasets`.`id_exp_ec_dataset`))) left join `isotopes` on((`exp_icpms_analyte_internalstandard`.`name_isotope_analyte` = `isotopes`.`name_isotope`))) left join `elements` `e` on((`isotopes`.`element` = `e`.`element`))) left join `exp_icpms` on((`exp_icpms_sfc_batch`.`id_exp_icpms` = `exp_icpms`.`id_exp_icpms`))) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `exp_icpms_sfc_expanded`
--

/*!50001 DROP VIEW IF EXISTS `exp_icpms_sfc_expanded`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `exp_icpms_sfc_expanded` AS select `exp_icpms`.`id_exp_icpms` AS `id_exp_icpms`,`exp_icpms`.`name_sample` AS `name_sample`,`exp_icpms`.`name_user` AS `name_user`,`exp_icpms`.`name_setup_icpms` AS `name_setup_icpms`,`exp_icpms`.`t_start__timestamp_icpms_pc` AS `t_start__timestamp_icpms_pc`,`exp_icpms`.`t_duration__s` AS `t_duration__s`,`exp_icpms`.`t_duration_planned__s` AS `t_duration_planned__s`,`exp_icpms`.`type_experiment` AS `type_experiment`,`exp_icpms`.`plasma_mode` AS `plasma_mode`,`exp_icpms`.`tune_mode` AS `tune_mode`,`exp_icpms`.`num_of_scans` AS `num_of_scans`,`exp_icpms`.`id_exp_icpms_calibration_set` AS `id_exp_icpms_calibration_set`,`exp_icpms`.`gas_dilution_factor` AS `gas_dilution_factor`,`exp_icpms`.`name_gas_collision` AS `name_gas_collision`,`exp_icpms`.`flow_rate_collision__mL_min` AS `flow_rate_collision__mL_min`,`exp_icpms`.`name_gas_reaction` AS `name_gas_reaction`,`exp_icpms`.`flow_rate_reaction__mL_min` AS `flow_rate_reaction__mL_min`,`exp_icpms`.`comment` AS `comment`,`exp_icpms`.`name_computer_inserted_data` AS `name_computer_inserted_data`,`exp_icpms`.`file_path_rawdata` AS `file_path_rawdata`,`exp_icpms`.`t_inserted_data__timestamp` AS `t_inserted_data__timestamp`,`exp_icpms`.`file_name_rawdata` AS `file_name_rawdata`,`exp_icpms`.`batch_name` AS `batch_name`,(`exp_icpms_sfc`.`t_start__timestamp_sfc_pc` - interval `exp_icpms_sfc`.`t_delay__s` second) AS `t_start_delaycorrected__timestamp_sfc_pc`,((`exp_icpms_sfc`.`t_start__timestamp_sfc_pc` - interval `exp_icpms_sfc`.`t_delay__s` second) + interval `exp_icpms`.`t_duration__s` second) AS `t_end_delaycorrected__timestamp_sfc_pc`,`exp_icpms_sfc`.`name_setup_sfc` AS `name_setup_sfc`,`exp_icpms_sfc`.`t_start__timestamp_sfc_pc` AS `t_start__timestamp_sfc_pc`,`exp_icpms_sfc`.`t_delay__s` AS `t_delay__s`,`exp_icpms_sfc`.`flow_rate_real__mul_min` AS `flow_rate_real__mul_min`,`exp_icpms_sfc`.`t_start_shift__s` AS `t_start_shift__s`,`exp_icpms_sfc`.`t_end_shift__s` AS `t_end_shift__s`,`exp_icpms_calibration_params`.`name_isotope_analyte` AS `name_isotope_analyte`,`exp_icpms_calibration_params`.`name_isotope_internalstandard` AS `name_isotope_internalstandard`,`exp_icpms_calibration_params`.`calibration_slope__countratio_mug_L` AS `calibration_slope__countratio_mug_L`,`exp_icpms_calibration_params`.`delta_calibration_slope__countratio_mug_L` AS `delta_calibration_slope__countratio_mug_L`,`exp_icpms_calibration_params`.`calibration_intercept__countratio` AS `calibration_intercept__countratio`,`exp_icpms_calibration_params`.`delta_calibration_intercept__countratio` AS `delta_calibration_intercept__countratio`,`exp_icpms_calibration_params`.`Rsquared` AS `Rsquared`,`exp_icpms_calibration_params`.`calibration_method` AS `calibration_method`,`exp_icpms_calibration_params`.`file_path_calibration_plot` AS `file_path_calibration_plot`,`exp_icpms_calibration_params`.`name_computer_inserted_data` AS `name_computer_inserted_calibration_data`,`exp_icpms_calibration_params`.`t_inserted_data__timestamp` AS `t_inserted_calibration_data__timestamp` from ((`exp_icpms` left join `exp_icpms_sfc` on((`exp_icpms`.`id_exp_icpms` = `exp_icpms_sfc`.`id_exp_icpms`))) join `exp_icpms_calibration_params` on((`exp_icpms`.`id_exp_icpms_calibration_set` = `exp_icpms_calibration_params`.`id_exp_icpms_calibration_set`))) where (`exp_icpms`.`type_experiment` = 'sfc-icpms') */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `match_exp_sfc_exp_icpms`
--

/*!50001 DROP VIEW IF EXISTS `match_exp_sfc_exp_icpms`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `match_exp_sfc_exp_icpms` AS select `ec`.`id_exp_sfc` AS `id_exp_sfc`,`ec`.`name_user` AS `name_user`,`ec`.`name_setup_sfc` AS `name_setup_sfc`,`ec`.`name_setup_sfc_alias` AS `name_setup_sfc_alias`,`ec`.`name_setup_sfc_feature` AS `name_setup_sfc_feature`,`ec`.`name_setup_sfc_type` AS `name_setup_sfc_type`,`ec`.`t_start__timestamp` AS `t_start__timestamp`,`ec`.`t_end__timestamp` AS `t_end__timestamp`,`ec`.`rawdata_path` AS `rawdata_path`,`ec`.`rawdata_computer` AS `rawdata_computer`,`ec`.`id_ML` AS `id_ML`,`ec`.`id_ML_technique` AS `id_ML_technique`,`ec`.`id_sample` AS `id_sample`,`ec`.`id_spot` AS `id_spot`,`ec`.`force__N` AS `force__N`,`ec`.`T_stage__degC` AS `T_stage__degC`,`ec`.`interrupted` AS `interrupted`,`ec`.`labview_sfc_version` AS `labview_sfc_version`,`ec`.`db_version` AS `db_version`,`ec`.`comment` AS `comment`,`ec`.`ec_name_technique` AS `ec_name_technique`,`ec`.`ec_R_u__ohm` AS `ec_R_u__ohm`,`ec`.`ec_iR_corr_in_situ__percent` AS `ec_iR_corr_in_situ__percent`,`ec`.`ec_R_u_determining_exp_ec` AS `ec_R_u_determining_exp_ec`,`ec`.`ec_E_RE__VvsRHE` AS `ec_E_RE__VvsRHE`,`ec`.`ec_name_RE` AS `ec_name_RE`,`ec`.`ec_name_RE_material` AS `ec_name_RE_material`,`ec`.`ec_name_RE_manufacturer` AS `ec_name_RE_manufacturer`,`ec`.`ec_name_RE_model` AS `ec_name_RE_model`,`ec`.`ec_name_CE` AS `ec_name_CE`,`ec`.`ec_name_CE_material` AS `ec_name_CE_material`,`ec`.`ec_name_CE_manufacturer` AS `ec_name_CE_manufacturer`,`ec`.`ec_name_CE_model` AS `ec_name_CE_model`,`ec`.`ec_name_device` AS `ec_name_device`,`ec`.`ec_id_control_mode` AS `ec_id_control_mode`,`ec`.`ec_id_ie_range` AS `ec_id_ie_range`,`ec`.`ec_id_vch_range` AS `ec_id_vch_range`,`ec`.`ec_id_ich_range` AS `ec_id_ich_range`,`ec`.`ec_id_vch_filter` AS `ec_id_vch_filter`,`ec`.`ec_id_ich_filter` AS `ec_id_ich_filter`,`ec`.`ec_id_ca_speed` AS `ec_id_ca_speed`,`ec`.`ec_id_ie_stability` AS `ec_id_ie_stability`,`ec`.`ec_id_sampling_mode` AS `ec_id_sampling_mode`,`ec`.`ec_ie_range_auto` AS `ec_ie_range_auto`,`ec`.`ec_vch_range_auto` AS `ec_vch_range_auto`,`ec`.`ec_ich_range_auto` AS `ec_ich_range_auto`,`ec`.`samples_id_sample` AS `samples_id_sample`,`ec`.`samples_name_sample` AS `samples_name_sample`,`ec`.`samples_name_user` AS `samples_name_user`,`ec`.`samples_t_manufactured__timestamp` AS `samples_t_manufactured__timestamp`,`ec`.`samples_comment` AS `samples_comment`,`ec`.`samples_total_loading__mg_cm2` AS `samples_total_loading__mg_cm2`,`ec`.`spots_id_spot` AS `spots_id_spot`,`ec`.`spots_spot_size__mm2` AS `spots_spot_size__mm2`,`ec`.`spots_pos_x__mm` AS `spots_pos_x__mm`,`ec`.`spots_pos_y__mm` AS `spots_pos_y__mm`,`ec`.`spots_comment` AS `spots_comment`,`ec`.`spots_total_loading__mg_cm2` AS `spots_total_loading__mg_cm2`,`ec`.`cv_E_initial__VvsRE` AS `cv_E_initial__VvsRE`,`ec`.`cv_E_apex1__VvsRE` AS `cv_E_apex1__VvsRE`,`ec`.`cv_E_apex2__VvsRE` AS `cv_E_apex2__VvsRE`,`ec`.`cv_E_final__VvsRE` AS `cv_E_final__VvsRE`,`ec`.`cv_scanrate__mV_s` AS `cv_scanrate__mV_s`,`ec`.`cv_stepsize__mV` AS `cv_stepsize__mV`,`ec`.`cv_cycles` AS `cv_cycles`,`ec`.`geis_f_initial__Hz` AS `geis_f_initial__Hz`,`ec`.`geis_f_final__Hz` AS `geis_f_final__Hz`,`ec`.`geis_I_dc__A` AS `geis_I_dc__A`,`ec`.`geis_I_amplitude__A` AS `geis_I_amplitude__A`,`ec`.`geis_R_initialguess__ohm` AS `geis_R_initialguess__ohm`,`ec`.`geis_points_per_decade` AS `geis_points_per_decade`,`ec`.`ghold_I_hold__A` AS `ghold_I_hold__A`,`ec`.`ghold_t_hold__s` AS `ghold_t_hold__s`,`ec`.`ghold_t_samplerate__s` AS `ghold_t_samplerate__s`,`ec`.`peis_f_initial__Hz` AS `peis_f_initial__Hz`,`ec`.`peis_f_final__Hz` AS `peis_f_final__Hz`,`ec`.`peis_E_dc__VvsRE` AS `peis_E_dc__VvsRE`,`ec`.`peis_E_amplitude__VvsRE` AS `peis_E_amplitude__VvsRE`,`ec`.`peis_R_initialguess__ohm` AS `peis_R_initialguess__ohm`,`ec`.`peis_points_per_decade` AS `peis_points_per_decade`,`ec`.`phold_E_hold__VvsRE` AS `phold_E_hold__VvsRE`,`ec`.`phold_t_hold__s` AS `phold_t_hold__s`,`ec`.`phold_t_samplerate__s` AS `phold_t_samplerate__s`,`ec`.`ppulse_E_hold1__VvsRE` AS `ppulse_E_hold1__VvsRE`,`ec`.`ppulse_E_hold2__VvsRE` AS `ppulse_E_hold2__VvsRE`,`ec`.`ppulse_t_hold1__s` AS `ppulse_t_hold1__s`,`ec`.`ppulse_t_hold2__s` AS `ppulse_t_hold2__s`,`ec`.`ppulse_t_samplerate__s` AS `ppulse_t_samplerate__s`,`ec`.`ppulse_cycles` AS `ppulse_cycles`,`ec`.`gpulse_I_hold1__A` AS `gpulse_I_hold1__A`,`ec`.`gpulse_I_hold2__A` AS `gpulse_I_hold2__A`,`ec`.`gpulse_t_hold1__s` AS `gpulse_t_hold1__s`,`ec`.`gpulse_t_hold2__s` AS `gpulse_t_hold2__s`,`ec`.`gpulse_t_samplerate__s` AS `gpulse_t_samplerate__s`,`ec`.`gpulse_cycles` AS `gpulse_cycles`,`ec`.`ramp_E_initial__VvsRE` AS `ramp_E_initial__VvsRE`,`ec`.`ramp_E_final__VvsRE` AS `ramp_E_final__VvsRE`,`ec`.`ramp_scanrate__mV_s` AS `ramp_scanrate__mV_s`,`ec`.`ramp_stepsize__mV` AS `ramp_stepsize__mV`,`ec`.`ramp_cycles` AS `ramp_cycles`,`ec`.`fc_top_name_flow_cell` AS `fc_top_name_flow_cell`,`ec`.`fc_top_name_flow_cell_name_user` AS `fc_top_name_flow_cell_name_user`,`ec`.`fc_top_name_flow_cell_material` AS `fc_top_name_flow_cell_material`,`ec`.`fc_top_name_flow_cell_A_opening_ideal__mm2` AS `fc_top_name_flow_cell_A_opening_ideal__mm2`,`ec`.`fc_top_name_flow_cell_A_opening_real__mm2` AS `fc_top_name_flow_cell_A_opening_real__mm2`,`ec`.`fc_top_name_flow_cell_manufacture_date` AS `fc_top_name_flow_cell_manufacture_date`,`ec`.`fc_top_name_flow_cell_CAD_file` AS `fc_top_name_flow_cell_CAD_file`,`ec`.`fc_top_name_flow_cell_comment` AS `fc_top_name_flow_cell_comment`,`ec`.`fc_top_id_sealing` AS `fc_top_id_sealing`,`ec`.`fc_top_id_sealing_name_user` AS `fc_top_id_sealing_name_user`,`ec`.`fc_top_id_sealing_material` AS `fc_top_id_sealing_material`,`ec`.`fc_top_id_sealing_A_sealing__mm2` AS `fc_top_id_sealing_A_sealing__mm2`,`ec`.`fc_top_id_sealing_A_opening__mm2` AS `fc_top_id_sealing_A_opening__mm2`,`ec`.`fc_top_id_sealing_thickness__mm` AS `fc_top_id_sealing_thickness__mm`,`ec`.`fc_top_id_sealing_shaping_method` AS `fc_top_id_sealing_shaping_method`,`ec`.`fc_top_id_sealing_comment` AS `fc_top_id_sealing_comment`,`ec`.`fc_top_id_PTL` AS `fc_top_id_PTL`,`ec`.`fc_top_id_PTL_name_user` AS `fc_top_id_PTL_name_user`,`ec`.`fc_top_id_PTL_material` AS `fc_top_id_PTL_material`,`ec`.`fc_top_id_PTL_thickness__mm` AS `fc_top_id_PTL_thickness__mm`,`ec`.`fc_top_id_PTL_manufacturer` AS `fc_top_id_PTL_manufacturer`,`ec`.`fc_top_id_PTL_A_PTL__mm2` AS `fc_top_id_PTL_A_PTL__mm2`,`ec`.`fc_top_id_PTL_shaping_method` AS `fc_top_id_PTL_shaping_method`,`ec`.`fc_top_id_PTL_comment` AS `fc_top_id_PTL_comment`,`ec`.`fc_bottom_name_flow_cell` AS `fc_bottom_name_flow_cell`,`ec`.`fc_bottom_name_flow_cell_name_user` AS `fc_bottom_name_flow_cell_name_user`,`ec`.`fc_bottom_name_flow_cell_material` AS `fc_bottom_name_flow_cell_material`,`ec`.`fc_bottom_name_flow_cell_A_opening_ideal__mm2` AS `fc_bottom_name_flow_cell_A_opening_ideal__mm2`,`ec`.`fc_bottom_name_flow_cell_A_opening_real__mm2` AS `fc_bottom_name_flow_cell_A_opening_real__mm2`,`ec`.`fc_bottom_name_flow_cell_manufacture_date` AS `fc_bottom_name_flow_cell_manufacture_date`,`ec`.`fc_bottom_name_flow_cell_CAD_file` AS `fc_bottom_name_flow_cell_CAD_file`,`ec`.`fc_bottom_name_flow_cell_comment` AS `fc_bottom_name_flow_cell_comment`,`ec`.`fc_bottom_id_sealing` AS `fc_bottom_id_sealing`,`ec`.`fc_bottom_id_sealing_name_user` AS `fc_bottom_id_sealing_name_user`,`ec`.`fc_bottom_id_sealing_material` AS `fc_bottom_id_sealing_material`,`ec`.`fc_bottom_id_sealing_A_sealing__mm2` AS `fc_bottom_id_sealing_A_sealing__mm2`,`ec`.`fc_bottom_id_sealing_A_opening__mm2` AS `fc_bottom_id_sealing_A_opening__mm2`,`ec`.`fc_bottom_id_sealing_thickness__mm` AS `fc_bottom_id_sealing_thickness__mm`,`ec`.`fc_bottom_id_sealing_shaping_method` AS `fc_bottom_id_sealing_shaping_method`,`ec`.`fc_bottom_id_sealing_comment` AS `fc_bottom_id_sealing_comment`,`ec`.`fc_bottom_id_PTL` AS `fc_bottom_id_PTL`,`ec`.`fc_bottom_id_PTL_name_user` AS `fc_bottom_id_PTL_name_user`,`ec`.`fc_bottom_id_PTL_material` AS `fc_bottom_id_PTL_material`,`ec`.`fc_bottom_id_PTL_thickness__mm` AS `fc_bottom_id_PTL_thickness__mm`,`ec`.`fc_bottom_id_PTL_manufacturer` AS `fc_bottom_id_PTL_manufacturer`,`ec`.`fc_bottom_id_PTL_A_PTL__mm2` AS `fc_bottom_id_PTL_A_PTL__mm2`,`ec`.`fc_bottom_id_PTL_shaping_method` AS `fc_bottom_id_PTL_shaping_method`,`ec`.`fc_bottom_id_PTL_comment` AS `fc_bottom_id_PTL_comment`,`ec`.`fe_top_id_pump_in` AS `fe_top_id_pump_in`,`ec`.`fe_top_id_pump_in_manufacturer` AS `fe_top_id_pump_in_manufacturer`,`ec`.`fe_top_id_pump_in_model` AS `fe_top_id_pump_in_model`,`ec`.`fe_top_id_pump_in_device` AS `fe_top_id_pump_in_device`,`ec`.`fe_top_id_tubing_in` AS `fe_top_id_tubing_in`,`ec`.`fe_top_id_tubing_in_name_tubing` AS `fe_top_id_tubing_in_name_tubing`,`ec`.`fe_top_id_tubing_in_inner_diameter__mm` AS `fe_top_id_tubing_in_inner_diameter__mm`,`ec`.`fe_top_id_tubing_in_color_code` AS `fe_top_id_tubing_in_color_code`,`ec`.`fe_top_id_tubing_in_manufacturer` AS `fe_top_id_tubing_in_manufacturer`,`ec`.`fe_top_id_tubing_in_model` AS `fe_top_id_tubing_in_model`,`ec`.`fe_top_pump_rate_in__rpm` AS `fe_top_pump_rate_in__rpm`,`ec`.`fe_top_id_pump_out` AS `fe_top_id_pump_out`,`ec`.`fe_top_id_pump_out_manufacturer` AS `fe_top_id_pump_out_manufacturer`,`ec`.`fe_top_id_pump_out_model` AS `fe_top_id_pump_out_model`,`ec`.`fe_top_id_pump_out_device` AS `fe_top_id_pump_out_device`,`ec`.`fe_top_id_tubing_out` AS `fe_top_id_tubing_out`,`ec`.`fe_top_id_tubing_out_name_tubing` AS `fe_top_id_tubing_out_name_tubing`,`ec`.`fe_top_id_tubing_out_inner_diameter__mm` AS `fe_top_id_tubing_out_inner_diameter__mm`,`ec`.`fe_top_id_tubing_out_color_code` AS `fe_top_id_tubing_out_color_code`,`ec`.`fe_top_id_tubing_out_manufacturer` AS `fe_top_id_tubing_out_manufacturer`,`ec`.`fe_top_id_tubing_out_model` AS `fe_top_id_tubing_out_model`,`ec`.`fe_top_pump_rate_out__rpm` AS `fe_top_pump_rate_out__rpm`,`ec`.`fe_top_flow_rate_real__mul_min` AS `fe_top_flow_rate_real__mul_min`,`ec`.`fe_top_name_electrolyte` AS `fe_top_name_electrolyte`,`ec`.`fe_top_c_electrolyte__mol_L` AS `fe_top_c_electrolyte__mol_L`,`ec`.`fe_top_T_electrolyte__degC` AS `fe_top_T_electrolyte__degC`,`ec`.`fe_bottom_id_pump_in` AS `fe_bottom_id_pump_in`,`ec`.`fe_bottom_id_pump_in_manufacturer` AS `fe_bottom_id_pump_in_manufacturer`,`ec`.`fe_bottom_id_pump_in_model` AS `fe_bottom_id_pump_in_model`,`ec`.`fe_bottom_id_pump_in_device` AS `fe_bottom_id_pump_in_device`,`ec`.`fe_bottom_id_tubing_in` AS `fe_bottom_id_tubing_in`,`ec`.`fe_bottom_id_tubing_in_name_tubing` AS `fe_bottom_id_tubing_in_name_tubing`,`ec`.`fe_bottom_id_tubing_in_inner_diameter__mm` AS `fe_bottom_id_tubing_in_inner_diameter__mm`,`ec`.`fe_bottom_id_tubing_in_color_code` AS `fe_bottom_id_tubing_in_color_code`,`ec`.`fe_bottom_id_tubing_in_manufacturer` AS `fe_bottom_id_tubing_in_manufacturer`,`ec`.`fe_bottom_id_tubing_in_model` AS `fe_bottom_id_tubing_in_model`,`ec`.`fe_bottom_pump_rate_in__rpm` AS `fe_bottom_pump_rate_in__rpm`,`ec`.`fe_bottom_id_pump_out` AS `fe_bottom_id_pump_out`,`ec`.`fe_bottom_id_pump_out_manufacturer` AS `fe_bottom_id_pump_out_manufacturer`,`ec`.`fe_bottom_id_pump_out_model` AS `fe_bottom_id_pump_out_model`,`ec`.`fe_bottom_id_pump_out_device` AS `fe_bottom_id_pump_out_device`,`ec`.`fe_bottom_id_tubing_out` AS `fe_bottom_id_tubing_out`,`ec`.`fe_bottom_id_tubing_out_name_tubing` AS `fe_bottom_id_tubing_out_name_tubing`,`ec`.`fe_bottom_id_tubing_out_inner_diameter__mm` AS `fe_bottom_id_tubing_out_inner_diameter__mm`,`ec`.`fe_bottom_id_tubing_out_color_code` AS `fe_bottom_id_tubing_out_color_code`,`ec`.`fe_bottom_id_tubing_out_manufacturer` AS `fe_bottom_id_tubing_out_manufacturer`,`ec`.`fe_bottom_id_tubing_out_model` AS `fe_bottom_id_tubing_out_model`,`ec`.`fe_bottom_pump_rate_out__rpm` AS `fe_bottom_pump_rate_out__rpm`,`ec`.`fe_bottom_flow_rate_real__mul_min` AS `fe_bottom_flow_rate_real__mul_min`,`ec`.`fe_bottom_name_electrolyte` AS `fe_bottom_name_electrolyte`,`ec`.`fe_bottom_c_electrolyte__mol_L` AS `fe_bottom_c_electrolyte__mol_L`,`ec`.`fe_bottom_T_electrolyte__degC` AS `fe_bottom_T_electrolyte__degC`,`ec`.`fg_top_Arring_name_gas` AS `fg_top_Arring_name_gas`,`ec`.`fg_top_Arring_flow_rate__mL_min` AS `fg_top_Arring_flow_rate__mL_min`,`ec`.`fg_top_purgevial_name_gas` AS `fg_top_purgevial_name_gas`,`ec`.`fg_top_purgevial_flow_rate__mL_min` AS `fg_top_purgevial_flow_rate__mL_min`,`ec`.`fg_top_main_name_gas` AS `fg_top_main_name_gas`,`ec`.`fg_top_main_flow_rate__mL_min` AS `fg_top_main_flow_rate__mL_min`,`ec`.`fg_bottom_Arring_name_gas` AS `fg_bottom_Arring_name_gas`,`ec`.`fg_bottom_Arring_flow_rate__mL_min` AS `fg_bottom_Arring_flow_rate__mL_min`,`ec`.`fg_bottom_purgevial_name_gas` AS `fg_bottom_purgevial_name_gas`,`ec`.`fg_bottom_purgevial_flow_rate__mL_min` AS `fg_bottom_purgevial_flow_rate__mL_min`,`ec`.`fg_bottom_main_name_gas` AS `fg_bottom_main_name_gas`,`ec`.`fg_bottom_main_flow_rate__mL_min` AS `fg_bottom_main_flow_rate__mL_min`,`ms`.`id_exp_icpms` AS `id_exp_icpms`,`ms`.`DATE(t_start_delaycorrected__timestamp_sfc_pc)` AS `DATE(t_start_delaycorrected__timestamp_sfc_pc)`,`ms`.`t_start_delaycorrected__timestamp_sfc_pc` AS `t_start_delaycorrected__timestamp_sfc_pc`,`ms`.`t_end_delaycorrected__timestamp_sfc_pc` AS `t_end_delaycorrected__timestamp_sfc_pc`,`ms`.`t_duration__s` AS `t_duration__s`,if((`ec`.`fe_top_id_pump_out_device` = 'ICP-MS'),'top',if((`ec`.`fe_bottom_id_pump_out_device` = 'ICP-MS'),'bottom',NULL)) AS `location` from (`exp_ec_expanded` `ec` join (select distinct `exp_icpms_sfc_expanded`.`id_exp_icpms` AS `id_exp_icpms`,`exp_icpms_sfc_expanded`.`name_user` AS `name_user`,`exp_icpms_sfc_expanded`.`name_setup_sfc` AS `name_setup_sfc`,cast(`exp_icpms_sfc_expanded`.`t_start_delaycorrected__timestamp_sfc_pc` as date) AS `DATE(t_start_delaycorrected__timestamp_sfc_pc)`,`exp_icpms_sfc_expanded`.`t_start_delaycorrected__timestamp_sfc_pc` AS `t_start_delaycorrected__timestamp_sfc_pc`,`exp_icpms_sfc_expanded`.`t_end_delaycorrected__timestamp_sfc_pc` AS `t_end_delaycorrected__timestamp_sfc_pc`,`exp_icpms_sfc_expanded`.`t_duration__s` AS `t_duration__s` from `exp_icpms_sfc_expanded`) `ms` on(((`ec`.`name_user` = `ms`.`name_user`) and (`ec`.`name_setup_sfc` = `ms`.`name_setup_sfc`) and (`ec`.`t_start__timestamp` < `ms`.`t_end_delaycorrected__timestamp_sfc_pc`) and (`ec`.`t_end__timestamp` > `ms`.`t_start_delaycorrected__timestamp_sfc_pc`)))) where (`ec`.`t_end__timestamp` is not null) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `spots_auto`
--

/*!50001 DROP VIEW IF EXISTS `spots_auto`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `spots_auto` AS select `a`.`id_sample` AS `id_sample`,`a`.`id_spot` AS `id_spot`,if((`a`.`id_sample` = `a`.`prev_id_sample`),(`a`.`pos_x__mm` - `a`.`prev_pos_x__mm`),0) AS `rel_x__mm`,if((`a`.`id_sample` = `a`.`prev_id_sample`),(`a`.`pos_y__mm` - `a`.`prev_pos_y__mm`),0) AS `rel_y__mm` from (select `spots`.`id_sample` AS `id_sample`,`spots`.`id_spot` AS `id_spot`,`spots`.`pos_x__mm` AS `pos_x__mm`,`spots`.`pos_y__mm` AS `pos_y__mm`,lag(`spots`.`pos_x__mm`) OVER (ORDER BY `spots`.`id_sample`,`spots`.`id_spot` )  AS `prev_pos_x__mm`,lag(`spots`.`pos_y__mm`) OVER (ORDER BY `spots`.`id_sample`,`spots`.`id_spot` )  AS `prev_pos_y__mm`,lag(`spots`.`id_sample`) OVER (ORDER BY `spots`.`id_sample`,`spots`.`id_spot` )  AS `prev_id_sample` from `spots` order by `spots`.`id_sample`,`spots`.`id_spot`) `a` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Current Database: `hte_data_documentation`
--

USE `hte_data_documentation`;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2023-12-14 12:18:55
