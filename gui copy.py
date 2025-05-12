from tkinter import filedialog, messagebox, ttk
from bom_pre_processing import *
from data_validation import *
from product_master import *
from data_loading import *
from save_output import *
from processing import *
from parameters import *
import tkinter as tk
# import warnings
import os


class OKM_processing:
    """ OKM Processing GUI """

    def __init__(self, root):
        """ Initialise the GUI """

        self.root = root
        self.root.title("OKM Processing")

        # Variable to store input file paths
        self.input_files = {'BOM': None,
                            'Prijslijst': None,
                            'Waste lijst': None,
                            'Actieve lijst': None}
        
        # Variable to store input Excel sheets
        self.selected_sheets = {'BOM': None,
                                'Prijslijst': None,
                                'Waste lijst': None,
                                'Actieve lijst': None}
        
        # Variable to store selected columns
        self.selected_columns = {'Prijslijst': None, 
                                 'Actieve lijst': None}

        # Variables to store datasets
        self.bom_data_raw = None
        self.price_weight_data = None
        self.waste_data = None
        self.active_rec_data = None

        # Varible to store datasets
        self.datasets = {}

        # Variables for Excel sheets selection dropdowns
        self.sheet_options = {'BOM': None,
                              'Prijslijst': None,
                              'Waste lijst': None,
                              'Actieve lijst': None}
        self.sheet_dropdowns = {'BOM': None,
                                'Prijslijst': None,
                                'Waste lijst': None,
                                'Actieve lijst': None}

        # Variables for column selection dropdowns
        self.column_options = {'Prijslijst': None, 
                               'Actieve lijst': None}
        self.column_dropdowns = {'Prijslijst': None, 
                                 'Actieve lijst': None}

        # Build the GUI
        self.build_gui()


    def build_gui(self):
        """ 
        Build the GUI

        The GUI consists of a number of widgets:
        - Input file selection: to select the input Excel files, and sheets
        - Data loading button: to run data loading
        - Column selection: to select the relevant columns for the processing
        - Data validation button: to run data validation
        - Processing button: to run processing
        """

        # Input Files Selection
        file_frame = tk.LabelFrame(self.root, text="Input Files", padx=10, pady=10)
        file_frame.pack(padx=10, pady=10, fill="x")

        self.file_labels = []

        i = 0
        for key in self.input_files.keys(): # TODO - test with more keys than 4
            # Excel file selection
            btn = tk.Button(file_frame, text=f"Select Input File {key}", command=lambda idx=i, key=key: self.select_input_file(key=key, index=idx))
            btn.grid(row=i, column=0, padx=5, pady=5, sticky="ew")
            label = tk.Label(file_frame, text="No file selected", anchor="w")
            label.grid(row=i, column=1, padx=5, pady=5, sticky="w")
            self.file_labels.append(label)

            # Excel sheet selection
            self.sheet_labels = []

            dropdown = ttk.Combobox(file_frame, state="disabled")
            dropdown.grid(row=i, column=2, padx=5, pady=5, sticky="ew")
            label = tk.Label(file_frame, text="Excel sheet", anchor="w")
            label.grid(row=i, column=3, padx=5, pady=5, sticky="w")
            self.sheet_labels.append(label)
            self.sheet_dropdowns[key] = dropdown
            
            i += 1
        
        # Data loading button
        # self.load_button = tk.Button(self.root, text="Load Data", command=self.load_data)
        # self.load_button.pack(pady=(10, 0))

        
        self.load_button = tk.Button(self.root, text="Load Data", command=self.load_data)
        self.load_button.grid(row=0, column=0, pady=(10, 0))
        
        self.load_progress = ttk.Progressbar(self.root, mode='determinate')
        self.load_progress.grid(row=0, column=1, pady=(10, 0))


        # Column Selection
        self.column_frame = tk.LabelFrame(self.root, text="Select Columns", padx=10, pady=10)
        self.column_frame.pack(padx=10, pady=10, fill="x")

        self.column_labels = []

        i = 0 
        for key in self.selected_columns.keys():
            label = tk.Label(self.column_frame, text=f"Select {key}")
            label.grid(row=i, column=0, padx=5, pady=5, sticky="w")
            dropdown = ttk.Combobox(self.column_frame, state="disabled")
            dropdown.grid(row=i, column=1, padx=5, pady=5, sticky="ew")
            self.column_labels.append(label)
            self.column_dropdowns[key] = dropdown
            i += 1

        # Data Validation Button
        self.validate_button = tk.Button(self.root, text="Run Data Validation", command=self.run_data_validation, state="disabled")
        self.validate_button.pack(pady=(10, 0))

        # Run Full Processing Button
        self.process_button = tk.Button(self.root, text="Run Full Processing", command=self.run_full_processing, state="disabled")
        self.process_button.pack(pady=(10, 0))
        self.progressbar = ttk.Progressbar(self.root, mode='determinate')
        self.progressbar.pack(pady=(10, 0))

        # Status Area
        status_frame = tk.LabelFrame(self.root, text="Status", padx=10, pady=10)
        status_frame.pack(padx=10, pady=10, fill="both", expand=True)

        self.status_text = tk.Text(status_frame, height=10, state="disabled")
        self.status_text.pack(fill="both", expand=True)


    def select_input_file(self, key, index):
        filepath = filedialog.askopenfilename(title="Select Excel File", filetypes=[("Excel files", "*.xlsx *.xls")])
        if filepath:
            self.input_files[key] = filepath
            self.file_labels[index].config(text=os.path.basename(filepath))
            self.update_status(f"Selected Input File {key}: {filepath}")

            self.sheet_options[key] = pd.ExcelFile(self.input_files[key]).sheet_names
            sheet_dropdown = self.sheet_dropdowns[key]
            sheet_dropdown.config(state="readonly", values=self.sheet_options[key])
            sheet_dropdown.set('')  # Clear selection - TODO double check this for desirability


    def load_data(self):
        """ Load the input data """

        try:
            # Check that input files and sheets have been selected
            file_warns= []
            sheet_warns = []

            for key in self.input_files.keys():
                file = self.input_files[key]
                if file == None:
                    file_warns.append(key)

            for key in self.selected_sheets.keys():
                sheet = self.sheet_dropdowns[key].get()
                if not sheet:
                    sheet_warns.append(key)
                    continue
                self.selected_sheets[key] = sheet

            if (not len(file_warns) == 0) or (not len(sheet_warns) == 0):
                file_warn = ""
                sheet_warn = ""

                if not len(file_warns) == 0:
                    file_warn = f'Please select input file(s) for: {", ".join(file_warns)}.'

                if not len(sheet_warns) == 0:
                    sheet_warn = f'Please select Excel sheet(s) for: {", ".join(sheet_warns)}'
                messagebox.showwarning("Missing Selection", f"{file_warn} {sheet_warn}")

            else:
                self.update_status("Loading data...")
                self.root.update() # TODO - see if all root.update() calls can be removed / replaced with root.update_idletasks()
                
                for key in self.selected_sheets:
                    data = load_input_file(self.input_files[key], self.selected_sheets[key], input_file_type=key)
                    self.datasets[key] = data
                    self.update_status(f"Loaded Input File: {key}")
        
        except Exception as e:
            messagebox.showerror("Error", f"Loading {key} failed: {e}")
            self.update_status(f"Loading error: {e}")

        # Update the dropdown menus for column selection
        for key in self.selected_columns:
            if key in  self.datasets.keys():
                self.column_options[key] = self.datasets[key].columns.to_list()
                dropdown = self.column_dropdowns[key]
                dropdown.config(state="readonly", values=self.column_options[key])
                dropdown.set('')  # Clear selection
        
        self.update_status("Data loading complete. Please select relevant columns")
        self.validate_button.config(state="normal")

    
    def run_data_validation(self):
        if not len([x for x in self.input_files.values() if x != None]) == 4:
            messagebox.showwarning("Missing File", "Please select all 4 input files before running validation.")
            return
        
        self.update_status("Validating Data...")
        self.root.update()

        try:
            # Check that columns have been selected
            for key in self.selected_columns.keys():
                col = self.column_dropdowns[key].get()
                if not col:
                    messagebox.showwarning("Missing Selection", f"Please select a column for: {key}.")
                    return
                self.selected_columns[key] = col

            # Carry out the data validation
            self.datasets['recipes'] = pre_process_bom(self.datasets['BOM'], 
                                                       self.datasets['Actieve lijst'], 
                                                       self.selected_columns['Actieve lijst'])
            
            self.datasets['ingredients'], self.datasets['packagings'], self.datasets['Hfs'] = process_product_master(self.datasets['recipes'])

            validate_data(self.datasets['ingredients'], 
                          self.datasets['Prijslijst'], 
                          self.selected_columns['Prijslijst'], 
                          self.datasets['recipes'], 
                          self.datasets['packagings'], 
                          self.datasets['Waste lijst'],
                          update_callback=self.update_status)

            self.update_status("Data validation complete. You can now process the data")
            self.process_button.config(state="normal")

        # except Exception as e:
        except ValueError as e:
            messagebox.showerror("Error", f"Validation failed: {e}")
            self.update_status(f"Validation error: {e}")


    def run_full_processing(self):
        self.update_status("Starting full processing...")
        self.root.update()

        try:
            recipes = process_recipes(self.datasets['recipes'],
                                      self.datasets['ingredients'],
                                      self.datasets['Hfs'],
                                      self.datasets['packagings'],
                                      self.datasets['Prijslijst'],
                                      self.selected_columns['Prijslijst'],
                                      req_cols_price_weight[0], # TODO - make this more dynamic in the parameters.py module (maybe use a dict?)
                                      self.datasets['Prijslijst'],
                                      self.datasets['Waste lijst'],
                                      update_progress = self.update_progress)

            self.update_status("Processing complete. Please select where to save output.")

            # Ask for output file location
            output_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx")],
                title="Save Output File"
            )
            if output_path:
                save_output(recipes=recipes, output_path=output_path)
                self.update_status(f"Output saved to {output_path}")
            else:
                self.update_status("Output saving cancelled.")

        except Exception as e:
            messagebox.showerror("Error", f"Processing failed: {e}")
            self.update_status(f"Processing error: {e}")


    def update_status(self, message):
        self.status_text.config(state="normal")
        self.status_text.insert(tk.END, message + "\n")
        self.status_text.see(tk.END)
        self.status_text.config(state="disabled")
        self.root.update_idletasks()
    

    def update_progress(self, value, maximum=None):
        if maximum is not None:
            self.progressbar["maximum"] = maximum
        self.progressbar["value"] = value
        self.root.update_idletasks()


if __name__ == "__main__":
    root = tk.Tk()
    app = OKM_processing(root)
    root.mainloop()