import re
import pyperclip
import tkinter as tk
from tkinter import scrolledtext, messagebox, font, ttk, Radiobutton, StringVar, Checkbutton, BooleanVar, Menu

def process_text(text, comment_option="hide", show_first=True, show_last=False):
    """Processes text based on selected options"""
    def process_word(match):
        word = match.group(0)
        if len(word) > 1:
            if show_first and show_last:
                # First letter + underscores + last letter
                return word[0] + '_' * (len(word) - 2) + word[-1]
            elif show_first:
                # First letter + underscores (default)
                return word[0] + '_' * (len(word) - 1)
            elif show_last:
                # Underscores + last letter
                return '_' * (len(word) - 1) + word[-1]
            else:
                # All underscores (fallback)
                return '_' * len(word)
        return word
    
    # Process each line separately
    lines = text.split('\n')
    processed_lines = []
    
    for line in lines:
        # Check if line contains comments
        if '//' in line:
            comment_index = line.find('//')
            code_part = line[:comment_index]
            comment_part = line[comment_index:]
            
            # Process code part
            processed_code = re.sub(r'\b\w+\b', process_word, code_part)
            
            # Handle comment part based on selected option
            if comment_option == "remove":
                # Remove comments completely
                processed_line = processed_code
            elif comment_option == "show":
                # Show comments unchanged
                processed_line = processed_code + comment_part
            elif comment_option == "hide":
                # Hide comments (process like regular text)
                processed_comment = re.sub(r'\b\w+\b', process_word, comment_part)
                processed_line = processed_code + processed_comment
            
        else:
            # Process line without comments
            processed_line = re.sub(r'\b\w+\b', process_word, line)
        
        # Only add non-empty lines or lines that have content
        processed_lines.append(processed_line)
    
    # Restore line breaks
    return '\n'.join(processed_lines)

def process_and_copy():
    """Processes text and copies to clipboard"""
    # Get text from input field
    input_text = input_text_area.get("1.0", tk.END).strip()
    
    if not input_text:
        messagebox.showwarning("Empty Input", "Please enter text to process")
        return
    
    try:
        # Get selected options
        comment_option = comment_var.get()
        show_first = first_letter_var.get()
        show_last = last_letter_var.get()
        
        # Process text with selected options
        processed_text = process_text(input_text, comment_option, show_first, show_last)
        
        # Show result
        output_text_area.delete("1.0", tk.END)
        output_text_area.insert("1.0", processed_text)
        
        # Copy to clipboard
        pyperclip.copy(processed_text)
        
        # Show success message
        messagebox.showinfo("Success", "Text processed and copied to clipboard!")
        
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

def process_only():
    """Processes text without copying to clipboard"""
    # Get text from input field
    input_text = input_text_area.get("1.0", tk.END).strip()
    
    if not input_text:
        messagebox.showwarning("Empty Input", "Please enter text to process")
        return
    
    try:
        # Get selected options
        comment_option = comment_var.get()
        show_first = first_letter_var.get()
        show_last = last_letter_var.get()
        
        # Process text with selected options
        processed_text = process_text(input_text, comment_option, show_first, show_last)
        
        # Show result
        output_text_area.delete("1.0", tk.END)
        output_text_area.insert("1.0", processed_text)
        
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

def paste_from_clipboard():
    """Pastes text from clipboard"""
    try:
        clipboard_text = pyperclip.paste()
        if clipboard_text:
            input_text_area.delete("1.0", tk.END)
            input_text_area.insert("1.0", clipboard_text)
        else:
            messagebox.showwarning("Clipboard", "Clipboard is empty")
    except Exception as e:
        messagebox.showerror("Error", f"Could not get text from clipboard: {str(e)}")

def clear_all():
    """Clears all fields"""
    input_text_area.delete("1.0", tk.END)
    output_text_area.delete("1.0", tk.END)

def on_key_press(event):
    """Handle key presses for universal shortcuts"""
    # Проверяем, что нажата Control/Command
    ctrl_pressed = (event.state & 0x4) != 0  # Control key on Windows/Linux
    cmd_pressed = (event.state & 0x8) != 0   # Command key on Mac
    shift_pressed = (event.state & 0x1) != 0  # Shift key
    
    if ctrl_pressed or cmd_pressed:
        widget = root.focus_get()
        if isinstance(widget, tk.Text):
            # Используем коды клавиш вместо символов
            keycode = event.keycode
            
            # Определяем буквенные клавиши по их физическому расположению
            # Клавиша 'A' (любая раскладка)
            if keycode in [38, 65, 97]:  # Разные коды для разных систем
                # Ctrl+A - Select All
                widget.tag_add(tk.SEL, "1.0", tk.END)
                widget.mark_set(tk.INSERT, "1.0")
                widget.see(tk.INSERT)
                return "break"
            
            # Клавиша 'C' (любая раскладка)
            elif keycode in [54, 67, 99]:  # Разные коды для разных систем
                # Ctrl+C - Copy
                try:
                    selected = widget.selection_get()
                    if selected:
                        pyperclip.copy(selected)
                except tk.TclError:
                    pass
                return "break"
            
            # Клавиша 'V' (любая раскладка)
            elif keycode in [55, 86, 118]:  # Разные коды для разных систем
                # Ctrl+V - Paste
                try:
                    # Check if text is selected to replace it
                    try:
                        selected = widget.selection_get()
                        if selected:
                            widget.delete(tk.SEL_FIRST, tk.SEL_LAST)
                    except tk.TclError:
                        pass
                    
                    clipboard_text = pyperclip.paste()
                    if clipboard_text:
                        widget.insert(tk.INSERT, clipboard_text)
                except Exception:
                    pass
                return "break"
    
    # Проверяем Shift+Insert для вставки (альтернативная комбинация)
    if shift_pressed and event.keycode == 108:  # Insert key
        widget = root.focus_get()
        if isinstance(widget, tk.Text):
            try:
                try:
                    selected = widget.selection_get()
                    if selected:
                        widget.delete(tk.SEL_FIRST, tk.SEL_LAST)
                except tk.TclError:
                    pass
                
                clipboard_text = pyperclip.paste()
                if clipboard_text:
                    widget.insert(tk.INSERT, clipboard_text)
            except Exception:
                pass
            return "break"
    
    # Проверяем Ctrl+Insert для копирования (альтернативная комбинация)
    if ctrl_pressed and event.keycode == 108:  # Insert key
        widget = root.focus_get()
        if isinstance(widget, tk.Text):
            try:
                selected = widget.selection_get()
                if selected:
                    pyperclip.copy(selected)
            except tk.TclError:
                pass
            return "break"
    
    return None

def create_context_menu(widget):
    """Create context menu for text widget"""
    context_menu = Menu(widget, tearoff=0)
    
    # Add menu items
    context_menu.add_command(label="Copy", 
                            command=lambda: copy_from_widget(widget),
                            accelerator="Ctrl+C")
    context_menu.add_command(label="Paste", 
                            command=lambda: paste_to_widget(widget),
                            accelerator="Ctrl+V")
    context_menu.add_command(label="Select All", 
                            command=lambda: select_all_in_widget(widget),
                            accelerator="Ctrl+A")
    context_menu.add_separator()
    context_menu.add_command(label="Clear", 
                            command=lambda: clear_widget(widget))
    
    # Bind right-click to show context menu
    widget.bind("<Button-3>", lambda e: show_context_menu(e, context_menu))
    
    return context_menu

def copy_from_widget(widget):
    """Copy text from widget to clipboard"""
    try:
        selected = widget.selection_get()
        if selected:
            pyperclip.copy(selected)
    except tk.TclError:
        pass

def paste_to_widget(widget):
    """Paste text from clipboard to widget"""
    try:
        # Check if text is selected to replace it
        try:
            selected = widget.selection_get()
            if selected:
                widget.delete(tk.SEL_FIRST, tk.SEL_LAST)
        except tk.TclError:
            pass
        
        clipboard_text = pyperclip.paste()
        if clipboard_text:
            widget.insert(tk.INSERT, clipboard_text)
    except Exception as e:
        print(f"Error pasting: {e}")

def select_all_in_widget(widget):
    """Select all text in widget"""
    widget.tag_add(tk.SEL, "1.0", tk.END)
    widget.mark_set(tk.INSERT, "1.0")
    widget.see(tk.INSERT)

def clear_widget(widget):
    """Clear all text in widget"""
    widget.delete("1.0", tk.END)

def show_context_menu(event, menu):
    """Show context menu at mouse position"""
    try:
        menu.tk_popup(event.x_root, event.y_root)
    finally:
        menu.grab_release()

def center_window(window, width, height):
    """Center the window on the screen"""
    # Get screen width and height
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    
    # Calculate position
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2 - 30
    
    # Set window position
    window.geometry(f'{width}x{height}+{x}+{y}')

def create_gui():
    """Creates the graphical interface"""
    global input_text_area, output_text_area, root
    global comment_var, first_letter_var, last_letter_var
    
    # Create main window
    root = tk.Tk()
    root.title("Text Hide Tool")
    
    # Set window size
    window_width = 900
    window_height = 650
    
    # Center window on screen
    center_window(root, window_width, window_height)
    
    # Configure fonts
    default_font = font.Font(family="Consolas", size=10)
    button_font = font.Font(family="Arial", size=10, weight="bold")
    options_font = font.Font(family="Arial", size=9)
    
    # Input Frame
    input_frame = tk.LabelFrame(root, text="Source Text", font=button_font, padx=10, pady=10)
    input_frame.pack(fill="both", expand=True, padx=20, pady=(10, 5))
    
    # Text area for input
    input_text_area = scrolledtext.ScrolledText(input_frame, height=8, font=default_font,
                                               wrap=tk.WORD, undo=True)
    input_text_area.pack(fill="both", expand=True)
    
    # Create context menu for input text area
    input_context_menu = create_context_menu(input_text_area)
    
    # Button panel for input
    input_button_frame = tk.Frame(input_frame)
    input_button_frame.pack(fill="x", pady=(5, 0))
    
    paste_btn = tk.Button(input_button_frame, text="Paste from Clipboard", 
                         command=paste_from_clipboard, font=button_font,
                         bg="#4CAF50", fg="white", padx=10)
    paste_btn.pack(side="left", padx=5)
    
    clear_input_btn = tk.Button(input_button_frame, text="Clear Field", 
                               command=lambda: input_text_area.delete("1.0", tk.END),
                               font=button_font, padx=10)
    clear_input_btn.pack(side="left", padx=5)
    
    # Middle section: Processing buttons and options
    middle_section = tk.Frame(root)
    middle_section.pack(pady=10, padx=20)
    
    # Left side of middle section: Processing buttons
    process_buttons_frame = tk.Frame(middle_section)
    process_buttons_frame.pack(side="left", padx=(0, 20))
    
    # Process only button
    process_only_btn = tk.Button(process_buttons_frame, text="PROCESS", 
                               command=process_only, font=button_font,
                               bg="#2196F3", fg="white", height=2, padx=20)
    process_only_btn.pack(side="left", padx=5)
    
    # Process and copy button
    process_copy_btn = tk.Button(process_buttons_frame, text="PROCESS AND COPY", 
                               command=process_and_copy, font=button_font,
                               bg="#FF9800", fg="white", height=2, padx=20)
    process_copy_btn.pack(side="left", padx=5)
    
    # Right side of middle section: Options frames
    options_container = tk.Frame(middle_section)
    options_container.pack(side="left", fill="both", expand=True)
    
    # Comments options frame (слева)
    comment_options_frame = tk.LabelFrame(options_container, text="Options for line comments (from '//' to end of line)", 
                                         font=("Arial", 9, "bold"), padx=10, pady=5)
    comment_options_frame.pack(side="left", fill="x", expand=True, padx=(0, 10))
    
    # Create variable for radiobuttons
    comment_var = StringVar(value="hide")  # Default value
    
    # Create radiobuttons in the specified order: hide, show, remove
    hide_rb = Radiobutton(comment_options_frame, text="Hide", 
                         variable=comment_var, value="hide", 
                         font=options_font)
    hide_rb.grid(row=0, column=0, padx=10, pady=3, sticky="w")
    
    show_rb = Radiobutton(comment_options_frame, text="Show", 
                         variable=comment_var, value="show", 
                         font=options_font)
    show_rb.grid(row=0, column=1, padx=10, pady=3, sticky="w")
    
    remove_rb = Radiobutton(comment_options_frame, text="Remove", 
                           variable=comment_var, value="remove", 
                           font=options_font)
    remove_rb.grid(row=0, column=2, padx=10, pady=3, sticky="w")
    
    # Letter display options frame (справа)
    letter_options_frame = tk.LabelFrame(options_container, text="Letter Display Options", 
                                        font=("Arial", 9, "bold"), padx=10, pady=5)
    letter_options_frame.pack(side="left", fill="x", expand=True)
    
    # Create variables for checkboxes
    first_letter_var = BooleanVar(value=True)  # Default: enabled
    last_letter_var = BooleanVar(value=False)  # Default: disabled
    
    # Create checkboxes
    first_cb = Checkbutton(letter_options_frame, text="Show first", 
                          variable=first_letter_var, font=options_font)
    first_cb.grid(row=0, column=0, padx=10, pady=3, sticky="w")
    
    last_cb = Checkbutton(letter_options_frame, text="Show last", 
                         variable=last_letter_var, font=options_font)
    last_cb.grid(row=0, column=1, padx=10, pady=3, sticky="w")
    
    # Output Frame
    output_frame = tk.LabelFrame(root, text="Processed Text", font=button_font, padx=10, pady=10)
    output_frame.pack(fill="both", expand=True, padx=20, pady=(5, 10))
    
    # Text area for output
    output_text_area = scrolledtext.ScrolledText(output_frame, height=8, font=default_font,
                                                wrap=tk.WORD, state="normal")
    output_text_area.pack(fill="both", expand=True)
    
    # Create context menu for output text area
    output_context_menu = create_context_menu(output_text_area)
    
    # Button panel for output
    output_button_frame = tk.Frame(output_frame)
    output_button_frame.pack(fill="x", pady=(5, 0))
    
    copy_btn = tk.Button(output_button_frame, text="Copy Result", 
                        command=lambda: pyperclip.copy(output_text_area.get("1.0", tk.END).strip()),
                        font=button_font, bg="#4CAF50", fg="white", padx=10)
    copy_btn.pack(side="left", padx=5)
    
    clear_output_btn = tk.Button(output_button_frame, text="Clear Field", 
                                command=lambda: output_text_area.delete("1.0", tk.END),
                                font=button_font, padx=10)
    clear_output_btn.pack(side="left", padx=5)
    
    # Bind универсальный обработчик нажатия клавиш для всего окна
    root.bind('<Key>', on_key_press)
    
    # Также привязываем к каждому текстовому виджету
    for widget in [input_text_area, output_text_area]:
        widget.bind('<Key>', on_key_press)
    
    # Start main loop
    root.mainloop()

def main():
    print("\nText Hide Tool - launching graphical interface...")
    
    try:
        create_gui()
    except ImportError as e:
        if "pyperclip" in str(e):
            print("\n❌ ERROR: pyperclip module not installed")
            print("Install it with: pip install pyperclip")
            input("Press Enter to exit...")
        else:
            raise e

if __name__ == "__main__":
    main()