import cmd
import json
import pandas as pd
import matplotlib.pyplot as plt

# TODO:
# - clean up presentation of tables
# - clean up data (ohp t1, e.g.)
# - enable option to see that entire day's workout
# - Add data of: volume for that body part and overall volume and volume for that exercise,
# - Add options for 1RM calculators


def convert_dates_to_pd_dts(df):
    df_copy = df.copy()
    df_copy.Date = pd.to_datetime(df_copy.Date)
    return df_copy


def one_rep_max(weight, reps, method="epley"):
    methods = {
        "epley": "weight * (1 + reps/30)",
    }
    return eval(methods[method])


def compute_all_1rm(df):
    df["1RM"] = df.apply(lambda row: one_rep_max(row["Weight"], row["Reps"]), axis=1)
    return df


def plot_weight_and_exercise_1rm(lift_data, weight_data, exercise_name):
    def on_pick(event):
        indexes = event.ind
        print("------------------------------------------")
        for index in indexes:
            print(lift_data.iloc[index])

    fig, weight_ax = plt.subplots()

    weight_ax.plot(weight_data["Date"], weight_df["Weight"])
    weight_ax.set_ylabel("Body weight (lbs)")
    weight_ax.legend(["Body weight"], loc="upper center")

    lift_ax = weight_ax.twinx()
    lift_ax.plot(lift_data["Date"], lift_data["1RM"], ".g", picker=True, pickradius=5)
    lift_ax.set_title(exercise_name)
    lift_ax.set_xlabel("Date")
    lift_ax.set_ylabel("Est. 1RM (lbs)")
    lift_ax.legend(["Weight lifted"], loc="best")

    fig.canvas.mpl_connect("pick_event", on_pick)
    plt.show()


class LiftDataShell(cmd.Cmd):
    def __init__(self, lift_data, weight_data):
        super(LiftDataShell, self).__init__()
        self.ld = lift_data
        self.ex_choices = {
            i: ex_name for i, ex_name in enumerate(self.ld["Exercise Name"].unique())
        }

        self.wd = weight_data

    intro = "Select an exercise. Type help or ? to see options."
    prompt = "\n\nSelect exercise: "

    def do_squat(self, arg):
        "See estimated 1RM and body weight for the squat over time."
        exercise_name = "Squat (Barbell)"
        single_exercise_data = self.ld.loc[self.ld["Exercise Name"] == exercise_name]
        plot_weight_and_exercise_1rm(single_exercise_data, self.wd, exercise_name)

    def do_bench(self, arg):
        "See estimated 1RM and body weight for the bench press over time."
        exercise_name = "Bench Press (Barbell)"
        single_exercise_data = self.ld.loc[self.ld["Exercise Name"] == exercise_name]
        plot_weight_and_exercise_1rm(single_exercise_data, self.wd, exercise_name)

    def do_deadlift(self, arg):
        "See estimated 1RM and body weight for the deadlift over time."
        exercise_name = "Deadlift (Barbell)"
        single_exercise_data = self.ld.loc[self.ld["Exercise Name"] == exercise_name]
        plot_weight_and_exercise_1rm(single_exercise_data, self.wd, exercise_name)

    def do_ohp(self, arg):
        "See estimated 1RM and body weight for the overhead press over time."
        exercise_name = "Overhead Press (Barbell)"
        single_exercise_data = self.ld.loc[self.ld["Exercise Name"] == exercise_name]
        plot_weight_and_exercise_1rm(single_exercise_data, self.wd, exercise_name)

    def do_more(self, arg):
        "See all other exercises for plotting 1RM and body weight over time."
        while True:
            print(json.dumps(self.ex_choices, indent=2))
            choice = input("Select number or type 'back' to return to previous menu: ")

            if choice in {"back", "exit"}:
                break

            choice = int(choice)
            if choice not in self.ex_choices:
                print("Invalid selection.")
            else:
                exercise_name = self.ex_choices[choice]
                single_exercise_data = self.ld.loc[
                    self.ld["Exercise Name"] == exercise_name
                ]
                plot_weight_and_exercise_1rm(
                    single_exercise_data, self.wd, exercise_name
                )

        if choice == "exit":
            return True

    def do_exit(self, arg):
        "Exit this program."
        return True


if __name__ == "__main__":
    lift_data = "data/strong.csv"
    weight_data = "data/mfp_data/weight.csv"

    lift_columns_to_ignore = [
        "Workout Name",
        "Duration",
        "Distance",
        "Seconds",
        "Notes",
        "Workout Notes",
        "RPE",
    ]

    lift_df = pd.read_csv(lift_data)
    weight_df = pd.read_csv(weight_data)
    lift_df.drop(columns=lift_columns_to_ignore, inplace=True)

    lift_data = convert_dates_to_pd_dts(lift_df)
    lift_data = compute_all_1rm(lift_data)
    weight_data = convert_dates_to_pd_dts(weight_df)

    shell = LiftDataShell(lift_data=lift_data, weight_data=weight_data)
    shell.cmdloop()
