import DatePicker from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";
import "../styles/datepicker.css";

interface CustomDatePickerProps {
    selected: string;
    onChange: (date: string) => void;
    className?: string;
    hasError?: boolean;
}

export default function CustomDatePicker({
    selected,
    onChange,
    className,
    hasError,
}: CustomDatePickerProps) {
    return (
        <div className="relative w-full">
            <DatePicker
                selected={selected ? new Date(selected) : null}
                onChange={(date: Date | null) => {
                    if (date) {
                        // Adjust for timezone offset to prevent day shifting
                        const offset = date.getTimezoneOffset();
                        const adjustedDate = new Date(date.getTime() - offset * 60 * 1000);
                        onChange(adjustedDate.toISOString().split("T")[0]);
                    }
                }}
                dateFormat="yyyy-MM-dd"
                className={className + (hasError ? " border-red-500" : "")}
                wrapperClassName="w-full"
                calendarClassName="custom-datepicker-calendar"
            />
            {/* Custom Icon (optional, if you want something specific over the default) */}
        </div>
    );
}
