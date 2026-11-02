# Student Performance Analysis & Data Visualization
# Created by Tarun Katara

import io
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

# Configure the dashboard page
st.set_page_config(page_title="Student Performance Analysis", page_icon="📊", layout="wide")

# Display project title and author
st.title("Student Performance Analysis")
st.caption("Upload a CSV or Excel file to analyze student marks. | Created by Tarun Katara")

# Explain the expected input format
st.write(
    "Upload a file with one row per student, one column for the student name/ID, "
    "and one or more columns containing subject marks."
)

# Let the user upload a CSV or Excel file
uploaded_file = st.file_uploader("Upload student data", type=["csv", "xlsx", "xls"])

def load_file(file):
    """Read the uploaded CSV or Excel file into a DataFrame."""
    if file.name.lower().endswith(".csv"):
        return pd.read_csv(file)
    return pd.read_excel(file)

def make_chart():
    """Create a Matplotlib figure and return it for display."""
    fig, ax = plt.subplots(figsize=(9, 4.5))
    return fig, ax

if uploaded_file is not None:
    try:
        # Read the uploaded file and remove completely empty rows and columns
        raw_df = load_file(uploaded_file)
        raw_df = raw_df.dropna(how="all").dropna(axis=1, how="all")

        if raw_df.empty:
            st.error("The uploaded file has no usable data.")
            st.stop()

        # Normalize column labels for display and mapping
        raw_df.columns = [str(col).strip() for col in raw_df.columns]

        st.subheader("1. Preview uploaded data")
        st.dataframe(raw_df.head(10), use_container_width=True)

        # Ask the user to map their own column names
        columns = raw_df.columns.tolist()
        name_col = st.selectbox("Select student name or ID column", columns)

        # Suggest numeric columns as possible subject columns
        possible_subjects = []
        for col in columns:
            if col != name_col:
                converted = pd.to_numeric(raw_df[col], errors="coerce")
                if converted.notna().sum() > 0:
                    possible_subjects.append(col)

        subject_cols = st.multiselect(
            "Select subject marks columns",
            options=possible_subjects,
            default=possible_subjects
        )

        # Set the grading rules used by the analysis
        settings_col1, settings_col2 = st.columns(2)
        with settings_col1:
            max_marks = st.number_input("Maximum marks per subject", min_value=1.0, value=100.0, step=1.0)
        with settings_col2:
            pass_marks = st.number_input(
                "Minimum passing percentage",
                min_value=0.0,
                max_value=100.0,
                value=35.0,
                step=1.0
            )

        # Run analysis only after the user selects valid columns
        if st.button("Analyze student performance", type="primary"):
            if not subject_cols:
                st.error("Select at least one subject marks column.")
                st.stop()

            # Keep only the selected student and subject columns
            df = raw_df[[name_col] + subject_cols].copy()
            df = df.rename(columns={name_col: "Student"})
            df["Student"] = df["Student"].astype("string").str.strip()

            # Convert subject marks to numbers; invalid or blank cells become missing values
            for subject in subject_cols:
                df[subject] = pd.to_numeric(df[subject], errors="coerce")

            # Count marks outside the allowed range before excluding them from calculations
            invalid_mask = (df[subject_cols] < 0) | (df[subject_cols] > max_marks)
            invalid_marks_count = int(invalid_mask.sum().sum())
            df[subject_cols] = df[subject_cols].mask(invalid_mask)

            # Remove rows without a student identifier or any valid subject mark
            df = df.dropna(subset=["Student"])
            df = df[df["Student"].str.len() > 0]
            df = df.dropna(subset=subject_cols, how="all")

            if df.empty:
                st.error("No valid student records were found. Check the selected columns and marks.")
                st.stop()

            # Calculate totals, average marks, percentage, and pass/fail status
            df["Subjects_Attempted"] = df[subject_cols].notna().sum(axis=1)
            df["Total_Marks"] = df[subject_cols].sum(axis=1, min_count=1)
            df["Average_Marks"] = df[subject_cols].mean(axis=1)
            df["Percentage"] = (df["Average_Marks"] / max_marks) * 100
            df["Result"] = df["Percentage"].ge(pass_marks).map({True: "Pass", False: "Fail"})

            # Rank students by average marks; tied scores receive the same rank
            df["Rank"] = df["Average_Marks"].rank(method="min", ascending=False).astype(int)
            df = df.sort_values(["Rank", "Student"])

            # Calculate dashboard summary metrics
            total_students = len(df)
            class_average = df["Percentage"].mean()
            pass_count = int((df["Result"] == "Pass").sum())
            fail_count = int((df["Result"] == "Fail").sum())
            pass_percentage = (pass_count / total_students) * 100
            topper = df.iloc[0]

            st.subheader("2. Performance summary")
            metric1, metric2, metric3, metric4 = st.columns(4)
            metric1.metric("Students analyzed", total_students)
            metric2.metric("Class average", f"{class_average:.2f}%")
            metric3.metric("Pass percentage", f"{pass_percentage:.2f}%")
            metric4.metric("Top performer", str(topper["Student"]))

            # Show the processed student-wise result table
            st.subheader("3. Student-wise results")
            st.dataframe(df, use_container_width=True)

            if invalid_marks_count:
                st.warning(
                    f"{invalid_marks_count} mark value(s) outside 0–{max_marks:g} "
                    "were excluded from calculations."
                )

            # Compare the top ten students using a horizontal bar chart
            st.subheader("4. Data visualizations")
            top_students = df.nlargest(min(10, total_students), "Average_Marks").sort_values("Average_Marks")
            fig, ax = make_chart()
            ax.barh(top_students["Student"].astype(str), top_students["Average_Marks"])
            ax.set_title("Top Students by Average Marks")
            ax.set_xlabel("Average Marks")
            ax.set_ylabel("Student")
            fig.tight_layout()
            st.pyplot(fig)
            plt.close(fig)

            # Compare average marks across the selected subjects
            subject_average = df[subject_cols].mean().sort_values(ascending=False)
            fig, ax = make_chart()
            ax.bar(subject_average.index.astype(str), subject_average.values)
            ax.set_title("Subject-wise Average Marks")
            ax.set_xlabel("Subject")
            ax.set_ylabel("Average Marks")
            ax.tick_params(axis="x", rotation=30)
            fig.tight_layout()
            st.pyplot(fig)
            plt.close(fig)

            # Show how student percentages are distributed
            fig, ax = make_chart()
            ax.hist(df["Percentage"], bins=10, edgecolor="black")
            ax.set_title("Distribution of Student Percentages")
            ax.set_xlabel("Percentage")
            ax.set_ylabel("Number of Students")
            fig.tight_layout()
            st.pyplot(fig)
            plt.close(fig)

            # Display the proportion of passing and failing students
            result_counts = df["Result"].value_counts().reindex(["Pass", "Fail"], fill_value=0)
            fig, ax = plt.subplots(figsize=(6, 4))
            ax.pie(
                result_counts.values,
                labels=result_counts.index,
                autopct="%1.1f%%",
                startangle=90
            )
            ax.set_title("Pass vs Fail")
            fig.tight_layout()
            st.pyplot(fig)
            plt.close(fig)

            # Let the user compare any two selected subjects
            if len(subject_cols) >= 2:
                scatter_col1, scatter_col2 = st.columns(2)
                with scatter_col1:
                    x_subject = st.selectbox("Scatter plot: X-axis subject", subject_cols, index=0)
                with scatter_col2:
                    y_subject = st.selectbox("Scatter plot: Y-axis subject", subject_cols, index=1)

                scatter_df = df[[x_subject, y_subject]].dropna()
                fig, ax = make_chart()
                ax.scatter(scatter_df[x_subject], scatter_df[y_subject])
                ax.set_title(f"{x_subject} vs {y_subject}")
                ax.set_xlabel(x_subject)
                ax.set_ylabel(y_subject)
                fig.tight_layout()
                st.pyplot(fig)
                plt.close(fig)

            # Prepare the analyzed results as a downloadable CSV file
            output = io.StringIO()
            df.to_csv(output, index=False)
            st.download_button(
                label="Download analyzed results (CSV)",
                data=output.getvalue(),
                file_name="student_performance_results.csv",
                mime="text/csv"
            )

            # Display the highest and lowest scoring student details
            st.subheader("5. Key findings")
            st.write(
                f"**Top performer:** {topper['Student']} "
                f"({topper['Percentage']:.2f}%)."
            )
            st.write(f"**Lowest average:** {df.loc[df['Average_Marks'].idxmin(), 'Student']} "
                     f"({df['Percentage'].min():.2f}%).")
            st.write(f"**Pass:** {pass_count} | **Fail:** {fail_count}")
            st.caption("Created by Tarun Katara")

    except Exception as error:
        # Show a readable message if the uploaded file cannot be processed
        st.error(f"Unable to process this file: {error}")
        st.info("Check that the file is a valid CSV/Excel file and contains a header row.")
else:
    # Show a sample file format when no upload has been made
    st.info(
        "Expected format: one student per row, a student name/ID column, "
        "and separate numeric columns for subject marks."
    )
    st.code(
        "Student,Maths,Science,English\n"
        "Amit,85,80,75\n"
        "Priya,95,90,85\n"
        "Rahul,70,75,80",
        language="csv"
    )
