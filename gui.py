from tkinter import filedialog, messagebox, ttk
from data_preparation import *
from save_output import *
from processing import *
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
        self.selected_columns = {'Prijs kolom': None, 
                                 'Actieve kolom': None}

        # Variables to store datasets
        self.bom_data_raw = None
        self.price_weight_data = None
        self.waste_data = None
        self.active_rec_data = None

        # Variables for dropdowns
        self.column_options = [[], []]
        self.column_dropdowns = [None, None]

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

        # Initial Validation Button
        self.validate_button = tk.Button(self.root, text="Run Initial Validation", command=self.run_initial_validation)
        self.validate_button.pack(pady=(10, 0))

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
            self.column_dropdowns[i] = dropdown
            i += 1

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

    
    def run_initial_validation(self):
        if not len([x for x in self.input_files.values() if x != None]) == 4:
            messagebox.showwarning("Missing File", "Please select all 4 input files before running validation.")
            return
        
        self.update_status("Running initial validation...")
        self.root.update()


        try:
            self.price_weight_data = load_price_data(self.input_files['Prijslijst'], "PriceList", ['INGREDIENT CODE', 'INGREDIENTS', 'KG'])
            self.waste_data = load_waste_data(self.input_files['Waste lijst'], 'WASTE', ['MEAL CODE', 'INGREDIENT CODE', 'WASTE-NAV', 'WASTE-FIN', 'WASTE-USE'])
            self.active_rec_data = load_active_rec_data(self.input_files['Actieve lijst'], "Actief", ['Artikel'])
            self.bom_data_raw = pd.read_excel(self.input_files['BOM'], sheet_name="Budget", skiprows=1, header=None, decimal=",")

            # Update dropdowns
            self.column_options[0] = self.price_weight_data.columns.to_list()
            self.column_options[1] = self.active_rec_data.columns.to_list()

            for i in range(2):
                dropdown = self.column_dropdowns[i]
                dropdown.config(state="readonly", values=self.column_options[i])
                dropdown.set('')  # Clear selection

            self.update_status("Validation complete. Please select columns.")
            self.process_button.config(state="normal")

        except Exception as e:
            messagebox.showerror("Error", f"Validation failed: {e}")
            self.update_status(f"Validation error: {e}")


    def run_full_processing(self):
        # Check that columns have been selected
        selected_columns = []
        for i in range(2):
            col = self.column_dropdowns[i].get()
            if not col:
                messagebox.showwarning("Missing Selection", f"Please select a column for File {i+1}.")
                return
            selected_columns.append(col)

        self.selected_columns = selected_columns

        self.update_status("Starting full processing...")
        self.root.update()

        try:
            recipes = processing(price_period=self.selected_columns[0], act_rec_period=self.selected_columns[1],
                                 bom_data_raw=self.bom_data_raw,
                                 price_weight_data=self.price_weight_data,
                                 waste_data=self.waste_data,
                                 active_rec_data=self.active_rec_data
                                 )

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