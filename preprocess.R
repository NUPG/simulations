read_TA_grades <- function(fn){
    raw_ta_grades <- read.csv(fn, header = TRUE, stringsAsFactors = FALSE)
    raw_ta_grades <- raw_ta_grades[,c(1, (ncol(raw_ta_grades)-3):ncol(raw_ta_grades))]
    return(raw_ta_grades)
}

match_submission_id <- function(){
    raw_ta_grades <- read.csv('TA_groundtruth_grades.csv', header = TRUE)
    subid_dict <- read.csv('UserID_Name_Dict.csv', header = FALSE)
}

convert_raw_TA <- function(raw_ta_grades, subid_dict, rubric_ids, overall_assignment_id){
    #output df
    #col1 submission id (subid_dict_id '_' overall_assignment_id '_' specific rubric id)
    #col2 average grade
    new_sub_id_col <- vector()
    avg_grade <- vector()
    num_rubric_elements <- length(rubric_ids)
    for(i in 1:nrow(raw_ta_grades)){
        subid_dict_id <- subid_dict[which(subid_dict[,2] == raw_ta_grades[i,1]), 1]
        for(j in 1:num_rubric_elements){
            new_sub_id_col <- c(new_sub_id_col, paste(subid_dict_id, overall_assignment_id, rubric_ids[j], sep = '_'))
            avg_grade <- c(avg_grade, raw_ta_grades[i,j+1])
        }
    }
    return(data.frame(new_sub_id_col, avg_grade))
}

generate_TA_groundtruth_array <- function(grades_fn, processed_TA_groundtruth_fn){
    grades <- read.csv(grades_fn, header = FALSE, stringsAsFactors = FALSE)
    processed_gt <- read.csv(processed_TA_groundtruth_fn, header = FALSE, stringsAsFactors = FALSE)
    order_of_submissions <- unique(grades[,2])
    gt_vec <- vector()
    for (sub in order_of_submissions) {
        if(sub %in% processed_gt[,1]){
            idx <- which(processed_gt[,1] == sub)
            gt_vec <- c(gt_vec, processed_gt[idx,2])
        } else {
            gt_vec <- c(gt_vec, -1)
        }
    }
    write.csv(gt_vec, 'gt_array.csv', row.names = FALSE)
}

project_proposal_info <- function(){
    rubric_ids <- c(7401,5559,4103,7177)
    overall_assignment_id <- 16271
    subid_dict <- read.csv('UserID_Name_Dict.csv', header = FALSE, stringsAsFactors = FALSE)
    raw_ta_grades <- read_TA_grades('TA_groundtruth_grades.csv')
    new_df <- convert_raw_TA(raw_ta_grades, subid_dict, rubric_ids, overall_assignment_id)
    write.csv(new_df, 'Processed_TA_groundtruth.csv', row.names = FALSE, col.names = FALSE)
}

generate_cv_folds_gt <- function(grades_fn, processed_TA_groundtruth_fn, num_folds = 3, num_rubric_elements = 4){
    grades <- read.csv(grades_fn, header = FALSE, stringsAsFactors = FALSE)
    processed_gt <- read.csv(processed_TA_groundtruth_fn, header = FALSE, stringsAsFactors = FALSE)
    
    num_obs <- nrow(processed_gt)/num_rubric_elements
    fold_size <- num_rubric_elements * (rep(floor(num_obs/num_folds), num_folds) + c(rep(1, num_obs%%num_folds), rep(0, num_folds - num_obs%%num_folds)))
    set.seed(10)
    perm <- sample.int(nrow(processed_gt))
    
    order_of_submissions <- unique(grades[,2])
    gt_vec <- vector()
    
    orig_gt <- processed_gt[,2]
    next_fold_start <- 1
    for (k in 1:num_folds) {
        gt_vec <- vector()
        processed_gt[perm[next_fold_start:(next_fold_start+fold_size[k]-1)],2] <- -1
        for (sub in order_of_submissions) {
            if(sub %in% processed_gt[,1]){
                idx <- which(processed_gt[,1] == sub)
                gt_vec <- c(gt_vec, processed_gt[idx,2])
            } else {
                gt_vec <- c(gt_vec, -1)
            }
        }
        next_fold_start <- next_fold_start+fold_size[k]
        processed_gt[,2] <- orig_gt
        
        new_gt_df <- data.frame(order_of_submissions, gt_vec)
        
        #write.csv(gt_vec, paste('gt_fold_', k, '.csv', sep = ''), row.names = FALSE)
        write.csv(new_gt_df, paste('gt_fold_', k, '.csv', sep = ''), row.names = FALSE)
    }
    
    
    
    #write.csv(gt_vec, 'gt_array.csv', row.names = FALSE)
}

compare_cv <- function(gt_fn, cv_fn_vec, num_rubric_elements = 4){
    #gt_fn <- processed_TA_groundtruth_fn
    #cv_fn_vec <- c('fold1.csv', 'fold2.csv', 'fold3.csv')
    
    processed_gt <- read.csv(gt_fn, header = FALSE, stringsAsFactors = FALSE)
    
    set.seed(10)
    perm <- sample.int(nrow(processed_gt))
    
    num_folds <- length(cv_fn_vec)
    num_obs <- nrow(processed_gt)/num_rubric_elements
    fold_size <- num_rubric_elements * (rep(floor(num_obs/num_folds), num_folds) + c(rep(1, num_obs%%num_folds), rep(0, num_folds - num_obs%%num_folds)))
    
    next_fold_start <- 1
    for (i in 1:num_folds){
        test_set_ids <- processed_gt[perm,1][next_fold_start:(next_fold_start + fold_size[i] - 1)]
        test_set_gt <- processed_gt[perm,2][next_fold_start:(next_fold_start + fold_size[i] - 1)]
        fold_estimate_df <- read.csv(cv_fn_vec[i], header = FALSE, stringsAsFactors = FALSE)
        test_set_est <- vector()
        for (id in test_set_ids){
            test_set_est <- c(test_set_est, fold_estimate_df[which(fold_estimate_df[,1] == id),2])
        }
        print(mean(abs(test_set_est - test_set_gt)))
        next_fold_start <- next_fold_start+fold_size[i]
    }
}