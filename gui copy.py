from tkinter import filedialog, messagebox, ttk
from bom_pre_processing import *
from data_validation import *
from product_master import *
from data_loading import *
from save_output import *
from processing import *
from parameters import *
import tkinter as tk
import warnings
import os


class OKM_processing:
    """ OKM Processing GUI """

    def __init__(self, root):
        self.root = root
        self.root.title("OKM Processing")

        # Variable to store file paths
        self.input_files = {'BOM': None,
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

        # Variables for dropdowns
        self.column_options = {'Prijslijst': None, 
                               'Actieve lijst': None}
        self.column_dropdowns = {'Prijslijst': None, 
                                 'Actieve lijst': None}

        # Build the GUI
        self.build_gui()


    def build_gui(self):
        # Input Files Selection
        file_frame = tk.LabelFrame(self.root, text="Select Input Files", padx=10, pady=10)
        file_frame.pack(padx=10, pady=10, fill="x")

        self.file_labels = []

        i = 0
        for key in self.input_files.keys():
            btn = tk.Button(file_frame, text=f"Select Input File {key}", command=lambda idx=i, key=key: self.select_input_file(key=key, index=idx))
            btn.grid(row=i, column=0, padx=5, pady=5, sticky="ew")
            label = tk.Label(file_frame, text="No file selected", anchor="w")
            label.grid(row=i, column=1, padx=5, pady=5, sticky="w")
            self.file_labels.append(label)
            i += 1

        # Column Selection (after validation)
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

        # Initial Validation Button
        self.validate_button = tk.Button(self.root, text="Run Data Validation", command=self.run_data_validation)
        self.validate_button.pack(pady=(10, 0))

        # Run Full Processing Button
        self.process_button = tk.Button(self.root, text="Run Full Processing", command=self.run_full_processing, state="disabled")
        self.process_button.pack(pady=(10, 0))

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

            # TODO - add a button to select input file sheet name from dropdown
            if key == 'BOM':
                sheet_name = "Budget"
            elif key == 'Prijslijst':
                sheet_name = "PriceList"
            elif key == 'Waste lijst':
                sheet_name = 'WASTE'
            elif key == 'Actieve lijst':
                sheet_name = "Actief"

            # TODO - add a visual indication of loading (e.g., graying out the UI, adding a loading wheel, or adding a progress bar)
            try:
                data = load_input_file(filepath, sheet_name, input_file_type=key)
                self.datasets[key] = data
                self.update_status(f"Loaded Input File: {key}")
            
            except Exception as e:
                messagebox.showerror("Error", f"Loading {key} failed: {e}")
                self.update_status(f"Loading error: {e}")

            # Update the dropdown menus for column selection once possible
            if (key == 'Prijslijst' or key == 'Actieve lijst') and ('data' in locals()):
                self.column_options[key] = self.datasets[key].columns.to_list()
                dropdown = self.column_dropdowns[key]
                dropdown.config(state="readonly", values=self.column_options[key])
                dropdown.set('')  # Clear selection

    
    def run_data_validation(self):
        if not len([x for x in self.input_files.values() if x != None]) == 4:
            messagebox.showwarning("Missing File", "Please select all 4 input files before running validation.")
            return
        
        self.update_status("Running data validation...")
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
                          self.datasets['Waste lijst'])

            self.update_status("Data validation complete. You can now process the data")
            self.process_button.config(state="normal")

        except Exception as e:
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
                                      self.datasets['Waste lijst'])

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


if __name__ == "__main__":
    root = tk.Tk()
    app = OKM_processing(root)
    root.mainloop()